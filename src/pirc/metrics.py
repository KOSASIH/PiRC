"""Advanced Metrics Collection"""

import asyncio
import time
from typing import Dict, List, Set
from collections import defaultdict

from prometheus_client import Gauge, Histogram, Counter
import structlog

from .config import settings

logger = structlog.get_logger("metrics")

class MetricsCollector:
    """Central metrics collector"""
    
    _instance = None
    _start_time = None
    _active_users: Set[str] = set()
    _user_activity: Dict[str, float] = {}
    
    ACTIVE_CONNECTIONS = Gauge('pirc_active_connections', 'Active IRC connections')
    MESSAGE_COUNT = Counter('pirc_messages_total', 'Total IRC messages', ['type'])
    COMMAND_COUNT = Counter('pirc_commands_total', 'Executed commands', ['command'])
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def startup(cls):
        """Initialize metrics on startup"""
        cls._start_time = time.time()
        logger.info("Metrics collector started")
        asyncio.create_task(cls._metrics_loop())
    
    @classmethod
    def shutdown(cls):
        """Cleanup on shutdown"""
        logger.info("Metrics collector stopped")
    
    @classmethod
    def uptime(cls) -> float:
        """Get uptime in seconds"""
        return time.time() - (cls._start_time or 0)
    
    @classmethod
    async def _metrics_loop(cls):
        """Background metrics collection"""
        while True:
            try:
                cls.ACTIVE_CONNECTIONS.set(len(cls._active_users))
                await asyncio.sleep(30)
            except Exception as e:
                logger.error("Metrics loop error", exc_info=e)
                await asyncio.sleep(60)
    
    @classmethod
    async def get_stats(cls) -> Dict:
        """Get comprehensive stats"""
        return {
            "active_users": len(cls._active_users),
            "uptime": cls.uptime(),
            "message_count": dict(cls.MESSAGE_COUNT._metrics),
            "command_count": dict(cls.COMMAND_COUNT._metrics)
        }
    
    @classmethod
    async def get_active_users(cls) -> List[str]:
        """Get currently active users"""
        now = time.time()
        expired = [user for user, last_seen in cls._user_activity.items() 
                  if now - last_seen > 300]  # 5min timeout
        for user in expired:
            cls._active_users.discard(user)
            del cls._user_activity[user]
        
        return list(cls._active_users)
    
    @classmethod
    def user_active(cls, user_id: str):
        """Mark user as active"""
        cls._active_users.add(user_id)
        cls._user_activity[user_id] = time.time()
    
    @classmethod
    def count_message(cls, msg_type: str):
        """Count message type"""
        cls.MESSAGE_COUNT.labels(type=msg_type).inc()
    
    @classmethod
    def count_command(cls, command: str):
        """Count executed command"""
        cls.COMMAND_COUNT.labels(command=command).inc()
