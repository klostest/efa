"""Matrix runner: a config describes cells; each cell is N games of one condition at one
level on one model. Every game is logged as one JSON line with both prompts and both raw
responses, so any number in a figure can be traced back to the text that produced it.

Conditions: the similarity twists in `mech/signal.py` (oracle / attributed oracle / claim /
symmetric claim) plus the `unknown` and `base` controls, between two LLM players or an LLM
and a scripted policy; `costly_claim` (D1), which adds a claim call before the game; and
`secret` (D2), where each player presents a code word and the cell fixes whether they match.
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import yaml
from tqdm import tqdm

from efa.agents.policy import Policy
from efa.game import pd
from efa.game.answer import Answer, AnswerError, parse_answer, sample_action
from efa.llm import Request, make_client
from efa.llm.cache import CachedClient
from efa.llm.mlx_client import FORCED_CLOSE, THINK_CLOSE
from efa.mech import costly, secret, signal

GAME_KEYS = ["A0", "A1"]


@dataclass
class Cell:
    cell_id: str
    condition: str  # "oracle" | "oracle_attributed" | "claim" | "claim_symmetric" | "unknown" | "base" | "costly_claim" | "secret"
    level: int | None  # similarity percentage, None for unknown/base
    model: str
    n_games: int
    policies: tuple[str, str] = ("llm", "llm")  # per player
    max_tokens: int = 800
    temperature: float = 1.0
    cot: bool = True
    thinking_budget: int | None = None  # native thinking on, cut at this many tokens
    # Added to the game index for the sample seed and the counterbalancing variant. Two
    # cells whose LLM prompts are byte-identical (e.g. honest vs honest and honest vs a
    # scripted invader: the honest player cannot see the partner) would otherwise share
    # cache keys, so the second cell would replay the first cell's decisions. An offset
    # makes them independent draws.
    sample_offset: int = 0
    # D1 only: the cost of the report, fixed per cell, or drawn per game from a range.
    cost: float | None = None
    cost_range: tuple[float, float] | None = None
    # D1 only: run the claim call and stop (the claim-rate sweep needs no game).
    claim_only: bool = False
    # D2 only: whether the two players' code words match in every game of the cell.
    match: bool | None = None


def expand_cells(cfg: dict) -> list[Cell]:
    cells = []
    for model in cfg["models"]:
        for cond in cfg["conditions"]:
            levels = cond.get("levels", [None])
            costs = cond.get("costs", [None])
            cost_range = tuple(cond["cost_range"]) if "cost_range" in cond else None
            if cond["name"] == "costly_claim":
                levels = [costly.CUE]
                if costs == [None] and cost_range is None:
                    raise ValueError("costly_claim needs `costs` or `cost_range`")
            match = None
            if cond["name"] == "secret":
                levels = [costly.CUE]
                if "match" not in cond:
                    raise ValueError("secret needs `match: true` or `match: false`")
                match = bool(cond["match"])
            for lvl in levels:
                for c in costs:
                    tag = f"{cond['name']}"
                    if cond["name"] == "costly_claim":
                        tag += f"_c{c:g}" if c is not None else f"_c{cost_range[0]:g}to{cost_range[1]:g}"
                    elif cond["name"] == "secret":
                        tag += "_match" if match else "_mismatch"
                    elif lvl is not None:
                        tag += f"_{lvl}"
                    if cond.get("claim_only"):
                        tag += "_claimonly"
                    pols = tuple(cond.get("policies", ["llm", "llm"]))
                    if pols != ("llm", "llm"):
                        tag += "_vs_" + pols[1] if pols[0] == "llm" else "_" + "_".join(pols)
                    short = model.split(":", 1)[-1].split("/")[-1]
                    cells.append(
                        Cell(
                            cell_id=f"{tag}__{short}",
                            condition=cond["name"],
                            level=lvl,
                            model=model,
                            n_games=cond.get("n_games", cfg.get("n_games", 30)),
                            policies=pols,
                            max_tokens=cfg.get("max_tokens", 800),
                            temperature=cfg.get("temperature", 1.0),
                            cot=cfg.get("cot", True),
                            thinking_budget=cfg.get("thinking_budget"),
                            sample_offset=cond.get("sample_offset", 0),
                            cost=None if c is None else float(c),
                            cost_range=cost_range,
                            claim_only=bool(cond.get("claim_only", False)),
                            match=match,
                        )
                    )
    return cells


def twist_for(cell: Cell) -> str | None:
    if cell.condition in signal.TWISTS:
        return signal.TWISTS[cell.condition](cell.level)
    if cell.condition == "unknown":
        return signal.unknown()
    if cell.condition == "base":
        return None
    raise ValueError(f"unknown condition {cell.condition!r}")


def cost_for_game(cell: Cell, g: int) -> float | None:
    """Fixed cost, or a per-game draw that depends only on the game index (so a rerun hits
    the cache). Drawn costs are rounded to two decimals so they read as money, not noise."""
    if cell.cost_range is None:
        return cell.cost
    lo, hi = cell.cost_range
    u = np.random.default_rng(7_919 + g + cell.sample_offset).random()
    return round(lo + (hi - lo) * u, 2)


def words_for_game(cell: Cell, g: int) -> tuple[str, str] | None:
    """D2: the code word each player presents in game g (None for other conditions)."""
    if cell.condition != "secret":
        return None
    return secret.words(g, bool(cell.match), cell.sample_offset)


def _request(cell: Cell, user: str, g: int, p: int, v: pd.Variant, stage: str) -> Request:
    return Request(
        system="",
        user=user,
        max_tokens=cell.max_tokens,
        temperature=cell.temperature,
        sample=g + cell.sample_offset,
        thinking_budget=cell.thinking_budget,
        answer_keys=tuple(costly.CLAIM_KEYS) if stage == "claim" else tuple(GAME_KEYS),
        tags={"coop_token": v.coop_token, "cell": cell.cell_id, "player": p, "stage": stage},
    )


def answer_text(text: str) -> str:
    """The part of a response to parse: what follows the last closed thinking block. The
    model drafts candidate JSON answers inside its thinking, and without this the parser
    could pick a draft when the real answer is missing (2026-10-26 D1 pilot)."""
    return text.rsplit(THINK_CLOSE, 1)[-1] if THINK_CLOSE in text else text


def build_requests(cell: Cell, claims: dict[tuple[int, int], bool] | None = None) -> list[tuple[int, int, Request | None, pd.Variant]]:
    """One entry per (game, player): the game request to send, or None for scripted players
    (and for games already excluded at the claim stage). `claims` is D1's realized reports."""
    out = []
    twist = twist_for(cell) if cell.condition not in ("costly_claim", "secret") else None
    for g in range(cell.n_games):
        v = pd.Variant.for_sample(g + cell.sample_offset)
        for p in (0, 1):
            if cell.policies[p] != "llm":
                out.append((g, p, None, v))
                continue
            if cell.condition == "costly_claim":
                if claims is None or (g, p) not in claims or (g, 1 - p) not in claims:
                    out.append((g, p, None, v))
                    continue
                tw = costly.game_twist(cost_for_game(cell, g), claims[(g, p)], claims[(g, 1 - p)])
            elif cell.condition == "secret":
                w = words_for_game(cell, g)
                tw = secret.game_twist(w[p], w[1 - p])
            else:
                tw = twist
            out.append((g, p, _request(cell, pd.full_prompt(v, p, tw, cot=cell.cot), g, p, v, "game"), v))
    return out


def build_claim_requests(cell: Cell) -> list[tuple[int, int, Request | None, pd.Variant]]:
    out = []
    for g in range(cell.n_games):
        v = pd.Variant.for_sample(g + cell.sample_offset)
        c = cost_for_game(cell, g)
        for p in (0, 1):
            if cell.policies[p] != "llm":
                out.append((g, p, None, v))
                continue
            out.append((g, p, _request(cell, costly.claim_prompt(v, p, c), g, p, v, "claim"), v))
    return out


def _answers(client, entries, keys: list[str], instruction: str) -> dict[tuple[int, int], dict]:
    """Send every request in `entries`, parse the JSON answer, retry the format once on a
    non-truncated failure, and return one record per (game, player)."""
    reqs = [e[2] for e in entries if e[2] is not None]
    comps = client.complete(reqs) if reqs else []
    it = iter(comps)
    parsed: dict[tuple[int, int], dict] = {}
    fix_reqs, fix_keys = [], []
    for g, p, req, v in entries:
        if req is None:
            continue
        c = next(it)
        rec = {"prompt": req.user, "response": c.text, "finish": c.finish_reason,
               "completion_tokens": c.completion_tokens, "cached": c.cached, "repaired": False,
               "fixed": False, "excluded": False, "truncated": False,
               "thinking_forced": FORCED_CLOSE in c.text}
        try:
            a = parse_answer(answer_text(c.text), keys)
            rec["probs"] = a.probs
            rec["repaired"] = a.repaired
        except AnswerError as e:
            rec["parse_error"] = str(e)
            if c.finish_reason == "length":
                # Reasoning was cut off. A format-fix on a truncated argument yields a
                # coin-flip answer, not a decision, so count it as truncated and exclude.
                rec["probs"], rec["excluded"], rec["truncated"] = None, True, True
                parsed[(g, p)] = rec
                continue
            fix_reqs.append(Request("", pd.format_fix_prompt(req.user, c.text, instruction),
                                    max_tokens=100, temperature=0.0, sample=g, tags=req.tags))
            fix_keys.append((g, p))
        parsed[(g, p)] = rec
    if fix_reqs:
        for key, c in zip(fix_keys, client.complete(fix_reqs)):
            rec = parsed[key]
            rec["fix_response"] = c.text
            try:
                a = parse_answer(answer_text(c.text), keys)
                rec["probs"], rec["repaired"], rec["fixed"] = a.probs, a.repaired, True
            except AnswerError as e:
                rec["probs"], rec["excluded"], rec["fix_error"] = None, True, str(e)
    return parsed


def _sample(probs: dict[str, float], rng: np.random.Generator) -> str:
    a = parse_answer(json.dumps({k: round(x * 100, 6) for k, x in probs.items()}), list(probs), tolerance=1)
    return sample_action(a, rng)


def run_cell(cell: Cell, client, rng: np.random.Generator, log) -> dict:
    t0 = time.time()
    n_players = range(2)

    # D1 stage 1: who reports. Scripted players (invaders, controls) always display the cue.
    claims: dict[tuple[int, int], bool] = {}
    claim_recs: dict[tuple[int, int], dict] = {}
    if cell.condition == "costly_claim":
        centries = build_claim_requests(cell)
        answered = _answers(client, centries, costly.CLAIM_KEYS, costly.CLAIM_OUTPUT_INSTRUCTION)
        for g, p, req, v in centries:
            if req is None:
                claims[(g, p)] = True
                claim_recs[(g, p)] = {"claim": True, "p_claim": 1.0}
                continue
            rec = answered[(g, p)]
            if rec.get("probs") is None:
                rec["claim"], rec["p_claim"] = None, None
            else:
                rec["p_claim"] = rec["probs"]["REPORT"]
                rec["claim"] = _sample(rec["probs"], rng) == "REPORT"
                claims[(g, p)] = rec["claim"]
            claim_recs[(g, p)] = rec

    # game stage
    entries = [] if cell.claim_only else build_requests(cell, claims if cell.condition == "costly_claim" else None)
    answered = _answers(client, entries, GAME_KEYS, pd.OUTPUT_INSTRUCTION)
    parsed: dict[tuple[int, int], dict] = {}
    for g in range(cell.n_games):
        for p in n_players:
            if (g, p) in answered:
                parsed[(g, p)] = {"policy": "llm"} | answered[(g, p)]
            elif cell.policies[p] != "llm":
                parsed[(g, p)] = {"policy": cell.policies[p], "response": None, "probs": None}
            else:  # LLM player with no game call: claim-only cell, or excluded at the claim stage
                parsed[(g, p)] = {"policy": "llm", "response": None, "probs": None,
                                  "excluded": not cell.claim_only}

    # second pass: sample actions, score, log
    n_ok = 0
    for g in range(cell.n_games):
        v = pd.Variant.for_sample(g + cell.sample_offset)
        c = cost_for_game(cell, g)
        recs = [parsed[(g, 0)], parsed[(g, 1)]]
        actions = []
        for p, rec in enumerate(recs):
            pol = Policy(cell.policies[p])
            if cell.claim_only:
                actions.append(None)
                rec["p_coop"] = None
            elif pol.fixed_action():
                actions.append(pol.fixed_action())
                rec["p_coop"] = 1.0 if pol.fixed_action() == "C" else 0.0
            elif rec.get("probs") is None:
                actions.append(None)
                rec["p_coop"] = None
            else:
                rec["p_coop"] = rec["probs"][v.coop_token]
                actions.append(v.action(_sample(rec["probs"], rng)))
        if cell.condition == "costly_claim":
            for p, rec in enumerate(recs):
                rec.update({f"claim_{k}" if k not in ("claim", "p_claim") else k: val
                            for k, val in claim_recs[(g, p)].items()})
            game_claims = (claims.get((g, 0)), claims.get((g, 1)))
        else:
            game_claims = None
        if cell.claim_only:
            excluded = any(cl is None for cl in game_claims)
            gross, pay = None, None
        else:
            excluded = any(a is None for a in actions)
            gross = pd.payoffs(actions[0], actions[1]) if not excluded else None
            pay = gross
            if gross is not None and cell.condition == "costly_claim":
                pay = costly.net_payoffs(gross, game_claims, c)
        n_ok += not excluded
        log.write(json.dumps({
            "cell": asdict(cell), "game": g, "variant": asdict(v), "actions": actions,
            "payoffs": pay, "gross_payoffs": gross, "cost": c, "claims": game_claims,
            "words": words_for_game(cell, g), "excluded": excluded,
            "players": [{k: val for k, val in r.items() if k not in ("prompt", "claim_prompt")}
                        | {"prompt": r.get("prompt"), "claim_prompt": r.get("claim_prompt")} for r in recs],
        }) + "\n")
    return {"cell": cell.cell_id, "games": cell.n_games, "ok": n_ok, "seconds": round(time.time() - t0, 1)}


def logged_games(log_path: Path) -> dict[str, int]:
    """Games already in the log, per cell id, so a rerun skips finished cells."""
    counts: dict[str, int] = {}
    if log_path.exists():
        with open(log_path) as f:
            for line in f:
                if line.strip():
                    cid = json.loads(line)["cell"]["cell_id"]
                    counts[cid] = counts.get(cid, 0) + 1
    return counts


def run_config(path: Path, out_dir: Path, only: str | None = None) -> list[dict]:
    cfg = yaml.safe_load(Path(path).read_text())
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "config.yaml").write_text(Path(path).read_text())
    cells = expand_cells(cfg)
    if only:
        cells = [c for c in cells if only in c.cell_id]
    rng = np.random.default_rng(cfg.get("seed", 0))
    summaries = []
    clients: dict[str, CachedClient] = {}
    done = logged_games(out_dir / "games.jsonl")
    with open(out_dir / "games.jsonl", "a") as log:
        for cell in tqdm(cells, desc="cells"):
            if done.get(cell.cell_id, 0) >= cell.n_games:
                s = {"cell": cell.cell_id, "games": cell.n_games, "skipped": "already logged"}
                summaries.append(s)
                tqdm.write(json.dumps(s))
                continue
            if cell.model not in clients:
                clients[cell.model] = CachedClient(
                    make_client(cell.model, **cfg.get("client", {})), out_dir / "cache.sqlite"
                )
            s = run_cell(cell, clients[cell.model], rng, log)
            summaries.append(s)
            tqdm.write(json.dumps(s))
    for c in clients.values():
        c.close()
    return summaries
