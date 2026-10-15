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
