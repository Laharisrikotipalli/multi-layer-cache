from app.lock import acquire_lock, wait_for_cache
from fastapi import FastAPI
from app.oracle import fetch_from_oracle
from app.redis_client import get_redis_client
from app.l1_cache import LRUCache
from app.metrics import metrics

import json

app = FastAPI()

# L1 Cache
l1_cache = LRUCache(capacity=3)

# L2 Cache
redis_client = get_redis_client()

@app.get("/")
def root():
    return {"message": "Multi-layer cache service running"}
@app.get("/data/{key}")
def get_data(key: str):
    # 1️⃣ Check L1 Cache
    l1_data = l1_cache.get(key)
    if l1_data:
        metrics.l1_hits += 1
        return l1_data

    # 2️⃣ Check Redis (L2 Cache)
    cached_data = redis_client.get(key)
    if cached_data:
        metrics.l2_hits += 1
        data = json.loads(cached_data)
        l1_cache.put(key, data)
        return data

    # 3️⃣ Cache miss → Try Redis lock
    acquired, lock_key = acquire_lock(redis_client, key)

    if acquired:
        # Leader request
        metrics.cache_misses += 1
        data = fetch_from_oracle(key)

        redis_client.setex(key, 30, json.dumps(data))
        l1_cache.put(key, data)

        redis_client.delete(lock_key)
        return data

    # 4️⃣ Non-leader → Wait for cache
    cached_data = wait_for_cache(redis_client, key)
    if cached_data:
        metrics.l2_hits += 1
        data = json.loads(cached_data)
        l1_cache.put(key, data)
        return data

    # 5️⃣ Fallback (very rare)
    metrics.cache_misses += 1
    return fetch_from_oracle(key)
@app.get("/metrics")
def get_metrics():
    return metrics.to_dict()


