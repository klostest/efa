"""SQLite cache in front of any client.

Key = sha256(model, system, user, max_tokens, temperature, sample[, thinking_budget]). A rerun of an identical
config costs zero model calls, and clearing the cache (delete the file) forces a fresh run,
which is how the event-day run is produced.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path

from efa.llm.base import Client, Completion, Request


def request_key(model: str, r: Request) -> str:
    payload = json.dumps(
        [model, r.system, r.user, r.max_tokens, r.temperature, r.sample]
        + ([r.thinking_budget] if r.thinking_budget else []),
        ensure_ascii=False,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class CachedClient:
    def __init__(self, inner: Client, path: Path | str):
        self.inner = inner
        self.model = inner.model
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.path)
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS completions ("
            "key TEXT PRIMARY KEY, model TEXT, text TEXT, prompt_tokens INTEGER, "
            "completion_tokens INTEGER, finish_reason TEXT)"
        )
        self.conn.commit()
        self.hits = 0
        self.misses = 0

    def _get(self, key: str) -> Completion | None:
        row = self.conn.execute(
            "SELECT model, text, prompt_tokens, completion_tokens, finish_reason "
            "FROM completions WHERE key = ?",
            (key,),
        ).fetchone()
        if row is None:
            return None
        return Completion(row[1], row[0], row[2], row[3], row[4], cached=True)

    def _put(self, key: str, c: Completion) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO completions VALUES (?, ?, ?, ?, ?, ?)",
            (key, c.model, c.text, c.prompt_tokens, c.completion_tokens, c.finish_reason),
        )

    def complete(self, requests: list[Request]) -> list[Completion]:
        keys = [request_key(self.model, r) for r in requests]
        out: list[Completion | None] = [self._get(k) for k in keys]
        todo = [i for i, c in enumerate(out) if c is None]
        self.hits += len(requests) - len(todo)
        self.misses += len(todo)
        if todo:
            fresh = self.inner.complete([requests[i] for i in todo])
            for i, c in zip(todo, fresh):
                out[i] = c
                self._put(keys[i], c)
            self.conn.commit()
        return out  # type: ignore[return-value]

    def close(self) -> None:
        self.conn.close()
