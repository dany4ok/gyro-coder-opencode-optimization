# Task 2 — Cache library (cachekit.py)

Implement module `cachekit.py` in the working directory root. Python standard library only.

Class `LRUCache`:

## Constructor
- `LRUCache(max_size, ttl=None, clock=None)`
- `max_size`: int >= 1, else `ValueError`.
- `ttl`: positive number (seconds) or None; `ttl <= 0` raises `ValueError`.
- `clock`: callable returning a float (current time in seconds). Default: `time.monotonic`. All time logic must use this clock (so tests can inject a fake clock).

## Operations
- `set(key, value)`: insert or overwrite; counts as an access (refreshes recency); TTL is measured from the time of `set`.
- `get(key, default=None)`: hit returns value and refreshes recency (does not reset TTL); miss returns default. If the entry is expired (`clock() >= entry.set_time + ttl`), it counts as a miss, is removed, and increments `expirations`.
- `delete(key)`: remove entry and return its value, or None if absent.
- `__contains__`, `__len__`: membership and current size (expired entries may remain until accessed or purged, but `len` must reflect live entries after `purge`).
- `keys()` and `items()`: current live entries (order unspecified); must not return expired entries once expired at access time is not guaranteed — define behavior: `keys()`/`items()` return entries present in the store regardless of expiry (this is acceptable).
- `purge()`: remove all expired entries, increment `expirations` once per removed entry, return the number removed.

## LRU eviction
When `set` would exceed `max_size`, evict the least-recently-accessed entry (access = `get` hit or `set`). Each eviction increments `evictions`.

## Stats
Attribute `stats`: dict with exactly these keys and integer counters: `hits`, `misses`, `evictions`, `expirations`.

## Thread safety
All operations must be safe under concurrent threads (no corrupted state, no lost updates). No external dependencies.

## Persistence
- `save(path)`: write a JSON file `{"entries": [{"key": ..., "value": ..., "expires_at": float|null}], "expires_at" is absolute expiry time (set_time + ttl) or null if no TTL, and "stats": {...current counters...}}`. Values must be JSON-serializable.
- `LRUCache.load(path, max_size, clock=None)`: classmethod returning a cache with `stats` restored from the file and entries restored in file order, dropping entries whose `expires_at` is not null and `<= clock()` at load time. `max_size` validation applies. Restored counters continue incrementing normally on subsequent operations (gets after load count as hits/misses).
