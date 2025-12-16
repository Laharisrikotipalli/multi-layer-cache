import time
import uuid

LOCK_TTL = 5  # seconds


def acquire_lock(redis_client, key):
    lock_key = f"lock:{key}"
    lock_value = str(uuid.uuid4())

    acquired = redis_client.set(
        lock_key,
        lock_value,
        nx=True,
        ex=LOCK_TTL
    )

    return acquired, lock_key


def wait_for_cache(redis_client, key, timeout=5):
    start = time.time()

    while time.time() - start < timeout:
        data = redis_client.get(key)
        if data:
            return data
        time.sleep(0.1)

    return None
