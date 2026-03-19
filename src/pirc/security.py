"""Advanced Security & Rate Limiting"""

import time
import hashlib
from typing import Dict, Optional
from collections import defaultdict

import redis.asyncio as redis
from pybloom_live import BloomFilter
import structlog

from .config import settings


class AdvancedRateLimiter:
    """Redis + Bloom Filter Rate Limiting"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.bans = BloomFilter(100000, 0.001)
        self.logger = structlog.get_logger("rate_limiter")
    
    async def is_banned(self, identifier: str) -> bool:
        """Check if user is banned using Bloom filter + Redis"""
        if identifier in self.bans:
            # Double-check with Redis (Bloom FP protection)
            ban_key = f"ban:{identifier}"
            banned = await self.redis.exists(ban_key)
            if banned:
                self.logger.warning("Ban check hit", identifier=identifier)
                return True
        return False
    
    async def track_command(self, identifier: str, command: str) -> bool:
        """Track command usage with sliding window"""
        if await self.is_banned(identifier):
            return False
        
        pipe = self.redis.pipeline()
        key = f"rate:{identifier}:{command}"
        window_key = f"window:{identifier}:{command}"
        
        now = int(time.time())
        pipe.zadd(key, {str(now): now})
        pipe.zremrangebyscore(key, 0, now - 60)  # 60s window
        pipe.expire(key, 120)
        pipe.incr(window_key)
        pipe.expire(window_key, 3600)
        
        results = await pipe.execute()
        count = await self.redis.zcard(key)
        
        if count > settings.max_commands_per_minute:
            await self.ban_user(identifier)
            return False
        
        self.logger.info("Command tracked", identifier=identifier, command=command, count=count)
        return True
    
    async def ban_user(self, identifier: str):
        """Ban user for configured duration"""
        await self.redis.setex(f"ban:{identifier}", settings.ban_duration_seconds, "1")
        self.bans.add(identifier)
        self.logger.warning("User banned", identifier=identifier, duration=settings.ban_duration_seconds)


class SecurityMiddleware:
    """Security middleware for all requests"""
    
    def __init__(self, redis_client: redis.Redis):
        self.rate_limiter = AdvancedRateLimiter(redis_client)
    
    async def check_request(self, user_id: str, command: str) -> bool:
        return await self.rate_limiter.track_command(user_id, command)
