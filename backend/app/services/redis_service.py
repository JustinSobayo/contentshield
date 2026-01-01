import json
from app.core.security import get_redis_client
import logging

logger = logging.getLogger(__name__)

class RedisService:
    def __init__(self):
        try:
            self.client = get_redis_client()
            # Rapid check to see if we can connect
            self.client.ping()
        except Exception:
            self.client = None
        self.ttl = 3600 * 24  # Cache for 24 hours

    def get_cached_analysis(self, key: str):
        if not self.client:
            return None
        try:
            data = self.client.get(key)
            if data:
                logger.info(f"Cache hit for key: {key}")
                return json.loads(data)
        except Exception as e:
            logger.error(f"Redis get error: {e}")
        return None

    def set_cached_analysis(self, key: str, data: dict):
        if not self.client:
            return
        try:
            self.client.setex(key, self.ttl, json.dumps(data))
        except Exception as e:
            logger.error(f"Redis set error: {e}")

redis_service = RedisService()
