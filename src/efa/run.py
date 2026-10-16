"""Matrix runner: a config describes cells; each cell is N games of one condition at one
level on one model. Every game is logged as one JSON line with both prompts and both raw
responses, so any number in a figure can be traced back to the text that produced it.

Week-1 scope: condition `c0` (oracle / attributed-oracle / claim twists, plus `unknown` and
`base` controls) between two LLM players, or between an LLM and a scripted policy for the
positive and negative controls.
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import yaml
from tqdm import tqdm

from efa.agents.policy import LLM, Policy
from efa.game import pd
from efa.game.answer import AnswerError, parse_answer, sample_action
from efa.llm import Request, make_client
from efa.llm.cache import CachedClient
from efa.llm.mlx_client import FORCED_CLOSE
from efa.mech import signal


@dataclass
class Cell:
    cell_id: str
    condition: str  # "oracle" | "oracle_attributed" | "claim" | "unknown" | "base"
    level: int | None  # similarity percentage, None for unknown/base
    model: str
    n_games: int
    policies: tuple[str, str] = ("llm", "llm")  # per player
    max_tokens: int = 800
    temperature: float = 1.0
    cot: bool = True
    thinking_budget: int | None = None  # native thinking on, cut at this many tokens


def expand_cells(cfg: dict) -> list[Cell]:
    cells = []
    for model in cfg["models"]:
        for cond in cfg["conditions"]:
            levels = cond.get("levels", [None])
            for lvl in levels:
                tag = f"{cond['name']}" + (f"_{lvl}" if lvl is not None else "")
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
                        policies=tuple(cond.get("policies", ["llm", "llm"])),
                        max_tokens=cfg.get("max_tokens", 800),
                        temperature=cfg.get("temperature", 1.0),
                        cot=cfg.get("cot", True),
                        thinking_budget=cfg.get("thinking_budget"),
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


def build_requests(cell: Cell) -> list[tuple[int, int, Request | None, pd.Variant]]:
    """One entry per (game, player): the request to send, or None for scripted players."""
    out = []
    twist = twist_for(cell)
    for g in range(cell.n_games):
        v = pd.Variant.for_sample(g)
        for p in (0, 1):
            if cell.policies[p] != "llm":
                out.append((g, p, None, v))
                continue
            req = Request(
                system="",
                user=pd.full_prompt(v, p, twist, cot=cell.cot),
                max_tokens=cell.max_tokens,
                temperature=cell.temperature,
                sample=g,
                thinking_budget=cell.thinking_budget,
                tags={"coop_token": v.coop_token, "cell": cell.cell_id, "player": p},
            )
            out.append((g, p, req, v))
    return out


def run_cell(cell: Cell, client, rng: np.random.Generator, log) -> dict:
    entries = build_requests(cell)
    reqs = [e[2] for e in entries if e[2] is not None]
    t0 = time.time()
    comps = client.complete(reqs) if reqs else []
    it = iter(comps)

    # first pass: parse, with one format-fix retry for failures
    parsed: dict[tuple[int, int], dict] = {}
    fix_reqs, fix_keys = [], []
    for g, p, req, v in entries:
        if req is None:
            parsed[(g, p)] = {"policy": cell.policies[p], "response": None, "probs": None}
            continue
        c = next(it)
        rec = {"policy": "llm", "prompt": req.user, "response": c.text, "finish": c.finish_reason,
               "completion_tokens": c.completion_tokens, "cached": c.cached, "repaired": False,
               "fixed": False, "excluded": False, "truncated": False,
               "thinking_forced": FORCED_CLOSE in c.text}
        try:
            a = parse_answer(c.text, ["A0", "A1"])
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
            fix_reqs.append(Request("", pd.format_fix_prompt(req.user, c.text), max_tokens=100,
                                    temperature=0.0, sample=g, tags=req.tags))
            fix_keys.append((g, p))
        parsed[(g, p)] = rec
    if fix_reqs:
        for key, c in zip(fix_keys, client.complete(fix_reqs)):
            rec = parsed[key]
            rec["fix_response"] = c.text
            try:
                a = parse_answer(c.text, ["A0", "A1"])
                rec["probs"], rec["repaired"], rec["fixed"] = a.probs, a.repaired, True
            except AnswerError as e:
                rec["probs"], rec["excluded"], rec["fix_error"] = None, True, str(e)

    # second pass: sample actions, score, log
    n_ok = 0
    for g in range(cell.n_games):
        v = pd.Variant.for_sample(g)
        recs = [parsed[(g, 0)], parsed[(g, 1)]]
        actions = []
        for p, rec in enumerate(recs):
            pol = Policy(cell.policies[p])
            if pol.fixed_action():
                actions.append(pol.fixed_action())
                rec["p_coop"] = 1.0 if pol.fixed_action() == "C" else 0.0
            elif rec.get("probs") is None:
                actions.append(None)
                rec["p_coop"] = None
            else:
                probs = rec["probs"]
                rec["p_coop"] = probs[v.coop_token]
                tok = sample_action(parse_answer(json.dumps({k: round(x * 100, 6) for k, x in probs.items()}), ["A0", "A1"], tolerance=1), rng)
                actions.append(v.action(tok))
        excluded = any(a is None for a in actions)
        pay = pd.payoffs(actions[0], actions[1]) if not excluded else (None, None)
        n_ok += not excluded
        log.write(json.dumps({
            "cell": asdict(cell), "game": g, "variant": asdict(v), "actions": actions,
            "payoffs": pay, "excluded": excluded,
            "players": [{k: val for k, val in r.items() if k != "prompt"} | {"prompt": r.get("prompt")} for r in recs],
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
