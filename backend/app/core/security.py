import redis
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.core.config import settings

def get_redis_client():
    return redis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)

try:
    # We'll rely on the lazy connection or a deferred ping.
    # Module-level blocking pings can delay startup and cause healthcheck failures.
    storage_uri = settings.REDIS_URL
except Exception as e:
    print(f"Warning: Redis config error ({e}). Falling back to memory storage.")
    storage_uri = "memory://"

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=storage_uri
)
