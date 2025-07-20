import redis
import json
from typing import Optional, Any
from app.config import settings

redis_client = redis.from_url(settings.redis_url)


class CacheService:
    def __init__(self):
        self.redis = redis_client

    def get(self, key: str) -> Optional[Any]:
        try:
            data = self.redis.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception:
            return None

    def set(self, key: str, value: Any, ttl: int = 300):
        try:
            self.redis.setex(key, ttl, json.dumps(value, default=str))
        except Exception:
            pass

    def delete(self, key: str):
        try:
            self.redis.delete(key)
        except Exception:
            pass


cache = CacheService()
