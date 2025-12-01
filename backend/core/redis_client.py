# backend/core/redis_client.py
import logging
from typing import Optional, Any
import time

logger = logging.getLogger(__name__)

class MockRedis:
    """
    Mock Redis client for development without Redis server - نسخه اصلاح شده
    """
    def __init__(self):
        self.data = {}
        self.expire_times = {}
        logger.info("🔄 Using Mock Redis - No Redis server required!")

    def ping(self) -> bool:
        """Simulate Redis ping"""
        return True

    def get(self, key: str) -> Optional[str]:
        """Simulate Redis get with expiration check"""
        current_time = time.time()
        if key in self.expire_times and current_time > self.expire_times[key]:
            del self.data[key]
            del self.expire_times[key]
            return None
        return self.data.get(key)

    def setex(self, key: str, time: int, value: Any) -> bool:
        """Simulate Redis setex with TTL - اصلاح شده"""
        self.data[key] = str(value)
        self.expire_times[key] = time.time() + time  # استفاده از time.time() نه time
        return True

    def delete(self, key: str) -> bool:
        """Simulate Redis delete"""
        if key in self.data:
            del self.data[key]
        if key in self.expire_times:
            del self.expire_times[key]
        return True

    def exists(self, key: str) -> bool:
        """Simulate Redis exists"""
        return key in self.data

    def close(self) -> None:
        """Simulate Redis close"""
        logger.debug("Mock Redis connection closed")

def get_redis_client() -> MockRedis:
    """
    Get Mock Redis client for development
    """
    return MockRedis()