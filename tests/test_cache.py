from efa.llm.base import Request
from efa.llm.cache import CachedClient
from efa.llm.fake import FakeClient


def test_cache_round_trip(tmp_path):
    inner = FakeClient(lambda r: f"echo:{r.user}:{r.sample}")
    c = CachedClient(inner, tmp_path / "cache.sqlite")
    reqs = [Request("sys", "hi", sample=i) for i in range(3)]
    first = c.complete(reqs)
    second = c.complete(reqs)
    assert [x.text for x in first] == [x.text for x in second]
    assert inner.calls == 3 and c.hits == 3 and c.misses == 3
    assert all(x.cached for x in second) and not any(x.cached for x in first)
    # a different sample index is a different key
    c.complete([Request("sys", "hi", sample=9)])
    assert inner.calls == 4


def test_thinking_budget_is_part_of_the_key(tmp_path):
    inner = FakeClient(lambda r: "x")
    c = CachedClient(inner, tmp_path / "cache.sqlite")
    c.complete([Request("", "hi"), Request("", "hi", thinking_budget=100), Request("", "hi", thinking_budget=200)])
    assert inner.calls == 3
    c.complete([Request("", "hi", thinking_budget=100)])
    assert inner.calls == 3 and c.hits == 1


def test_cached_client_commits_each_chunk(tmp_path):
    """Uncached requests go to the inner client in chunks, each committed before the next."""
    from efa.llm.cache import CachedClient
    from efa.llm.fake import FakeClient

    class Counting(FakeClient):
        sizes: list[int] = []

        def complete(self, requests):
            self.sizes.append(len(requests))
            return super().complete(requests)

    inner = Counting(lambda r: "x")
    cc = CachedClient(inner, tmp_path / "c.sqlite", chunk_size=2)
    reqs = [Request(system="", user=f"q{i}", max_tokens=50, temperature=1.0, sample=i) for i in range(5)]
    out = cc.complete(reqs)
    assert len(out) == 5 and inner.sizes == [2, 2, 1]
    assert cc.conn.execute("SELECT COUNT(*) FROM completions").fetchone()[0] == 5
    inner.sizes.clear()
    assert all(c.cached for c in cc.complete(reqs)) and inner.sizes == []
