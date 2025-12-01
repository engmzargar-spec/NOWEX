# backend/core/redis_mock.py
import logging

logger = logging.getLogger(__name__)

# داده global و persistent برای تمام instances
_global_redis_data = {}
_global_expire_times = {}

class MockRedisSimple:
    """
    Mock Redis با داده persistent بین درخواست‌ها
    """
    
    def __init__(self):
        self.data = _global_redis_data  # استفاده از داده global
        self.expire_times = _global_expire_times
        logger.info("🔄 Using GLOBAL Mock Redis - Data persists between requests!")

    def ping(self):
        return True

    def get(self, key):
        # چک انقضا
        if key in self.expire_times:
            import time
            if time.time() > self.expire_times[key]:
                del self.data[key]
                del self.expire_times[key]
                return None
        return self.data.get(key)

    def setex(self, key, ttl, value):
        import time
        self.data[key] = str(value)
        self.expire_times[key] = time.time() + ttl
        print(f"✅ GLOBAL Mock Redis: Stored {key} with value '{value}' (Persistent between requests)")
        return True

    def delete(self, key):
        if key in self.data:
            del self.data[key]
        if key in self.expire_times:
            del self.expire_times[key]
        return True

    def exists(self, key):
        return key in self.data

    def close(self):
        pass

def get_redis_simple():
    return MockRedisSimple()