# security/rate_limiter.py - Redis + Bloom Filter
import redis.asyncio as redis
import pybloom_live  # Probabilistic filtering
import asyncio
from typing import TypedDict

class AdvancedRateLimiter:
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url)
        self.bans = pybloom_live.BloomFilter(1000000, 0.001)
    
    async def check_user(self, user: str, cmd: str) -> bool:
        key = f"rate:{user}:{cmd}"
        count = await self.redis.incr(key)
        if count == 1:
            await self.redis.expire(key, 60)
        
        if count > 10:  # Sliding window
            await self.redis.setex(f"ban:{user}", 3600, "1")
            self.bans.add(user)
            return False
        return True
