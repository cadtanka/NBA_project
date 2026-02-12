import redis
import json

r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

def cache_get(key):
    data = r.get(key)
    return json.loads(data) if data else None

def cache_set(key, value, expire=3600):
    r.set(key, json.dumps(value), ex=expire)

def cache_delete_platform(pattern: str):
    """
    Deletes all keys matching a pattern
    Used for cache invalidation
    """

    for key in r.scan_iter(pattern):
        r.delete(key)