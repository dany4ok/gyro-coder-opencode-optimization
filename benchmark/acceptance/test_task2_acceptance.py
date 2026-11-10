"""External acceptance tests for Task 2 (cachekit.py). Read-only for agents."""
import json
import os
import sys
import threading

import pytest

TASK_DIR = os.environ.get("BENCH_TASK_DIR")
if not TASK_DIR:
    pytest.skip("BENCH_TASK_DIR not set", allow_module_level=True)
sys.path.insert(0, TASK_DIR)

from cachekit import LRUCache


class FakeClock:
    def __init__(self, t=0.0):
        self.t = t

    def __call__(self):
        return self.t

    def advance(self, dt):
        self.t += dt


def test_set_get_basic():
    c = LRUCache(2)
    c.set("a", 1)
    assert c.get("a") == 1
    assert c.get("missing") is None
    assert c.get("missing", "dflt") == "dflt"


def test_stats_hits_and_misses():
    c = LRUCache(2)
    c.set("a", 1)
    c.get("a")
    c.get("nope")
    assert c.stats["hits"] == 1
    assert c.stats["misses"] == 1
    assert set(c.stats.keys()) == {"hits", "misses", "evictions", "expirations"}


def test_lru_eviction_evicts_least_recently_used():
    clock = FakeClock()
    c = LRUCache(2, clock=clock)
    c.set("a", 1)
    c.set("b", 2)
    c.set("c", 3)
    assert "a" not in c
    assert c.get("b") == 2
    assert c.get("c") == 3
    assert c.stats["evictions"] == 1


def test_get_refreshes_recency():
    clock = FakeClock()
    c = LRUCache(2, clock=clock)
    c.set("a", 1)
    c.set("b", 2)
    c.get("a")
    c.set("c", 3)
    assert "b" not in c
    assert c.get("a") == 1


def test_set_existing_key_refreshes_recency():
    clock = FakeClock()
    c = LRUCache(2, clock=clock)
    c.set("a", 1)
    c.set("b", 2)
    c.set("a", 10)
    c.set("c", 3)
    assert "b" not in c
    assert c.get("a") == 10


def test_ttl_expiry_lazy_on_get():
    clock = FakeClock()
    c = LRUCache(2, ttl=10, clock=clock)
    c.set("a", 1)
    clock.advance(9)
    assert c.get("a") == 1
    clock.advance(1)  # now clock == set_time + ttl -> expired
    assert c.get("a") is None
    assert c.stats["expirations"] == 1
    assert c.stats["misses"] == 1


def test_get_does_not_reset_ttl():
    clock = FakeClock()
    c = LRUCache(2, ttl=10, clock=clock)
    c.set("a", 1)
    clock.advance(9)
    c.get("a")
    clock.advance(1)
    assert c.get("a") is None


def test_purge_removes_expired():
    clock = FakeClock()
    c = LRUCache(3, ttl=10, clock=clock)
    c.set("a", 1)
    c.set("b", 2)
    clock.advance(11)
    c.set("c", 3)
    removed = c.purge()
    assert removed == 2
    assert c.stats["expirations"] == 2
    assert c.get("a") is None
    assert c.get("c") == 3


def test_delete():
    c = LRUCache(2)
    c.set("a", 1)
    assert c.delete("a") == 1
    assert c.get("a") is None
    assert c.delete("a") is None


def test_len_keys_items_contains():
    c = LRUCache(5)
    c.set("a", 1)
    c.set("b", 2)
    assert len(c) == 2
    assert "a" in c
    assert "zz" not in c
    assert set(c.keys()) == {"a", "b"}
    assert dict(c.items()) == {"a": 1, "b": 2}


def test_max_size_validation():
    with pytest.raises(ValueError):
        LRUCache(0)
    with pytest.raises(ValueError):
        LRUCache(-3)


def test_ttl_validation():
    with pytest.raises(ValueError):
        LRUCache(5, ttl=0)
    with pytest.raises(ValueError):
        LRUCache(5, ttl=-1)


def test_thread_safety():
    c = LRUCache(50)
    errors = []

    def worker(tid):
        try:
            for i in range(200):
                c.set(f"k{tid}-{i}", i)
                c.get(f"k{tid}-{i % 40}")
        except Exception as exc:  # pragma: no cover
            errors.append(exc)

    threads = [threading.Thread(target=worker, args=(t,)) for t in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert not errors
    assert len(c) <= 50
    assert c.stats["hits"] + c.stats["misses"] == 8 * 200


def test_persistence_roundtrip(tmp_path):
    clock = FakeClock()
    c = LRUCache(3, ttl=100, clock=clock)
    c.set("a", {"nested": [1, 2]})
    c.set("b", "txt")
    c.get("a")
    c.get("zz")
    path = str(tmp_path / "cache.json")
    c.save(path)
    loaded = LRUCache.load(path, max_size=3, clock=clock)
    assert loaded.get("a") == {"nested": [1, 2]}
    assert loaded.get("b") == "txt"
    assert loaded.stats["hits"] == 3   # 1 restored from saved file + 2 hits after load
    assert loaded.stats["misses"] == 1


def test_load_drops_expired_entries(tmp_path):
    clock = FakeClock()
    c = LRUCache(2, ttl=10, clock=clock)
    c.set("a", 1)
    path = str(tmp_path / "cache.json")
    c.save(path)
    clock.advance(11)
    loaded = LRUCache.load(path, max_size=2, clock=clock)
    assert loaded.get("a") is None
    assert len(loaded.keys()) == 0


def test_save_file_is_valid_json(tmp_path):
    c = LRUCache(2)
    c.set("a", 1)
    path = str(tmp_path / "cache.json")
    c.save(path)
    doc = json.loads(open(path, encoding="utf-8").read())
    assert doc["entries"][0]["key"] == "a"
    assert doc["entries"][0]["value"] == 1
    assert doc["entries"][0]["expires_at"] is None
    assert doc["stats"]["hits"] == 0


def test_lru_access_order_evicts_least_recently_accessed():
    clock = FakeClock()
    c = LRUCache(2, ttl=10, clock=clock)
    c.set("a", 1)
    c.set("b", 2)
    c.get("a")          # access order: a refreshed, so b becomes least recent
    c.set("c", 3)       # evicts b
    assert "b" not in c
    assert c.get("a") == 1
    assert c.get("c") == 3
    clock.advance(10)   # ttl expires for both survivors (>= boundary)
    assert c.get("a") is None
    assert c.get("c") is None
