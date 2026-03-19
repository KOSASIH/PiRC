"""🚀 PiRC-AI-SUITE Main Orchestrator"""

import asyncio
import signal
import sys
from contextlib import asynccontextmanager

import structlog
from prometheus_client import start_http_server, Gauge, Counter

from .config import settings
from .api.main import app
from .metrics import MetricsCollector
from .security import SecurityMiddleware

# Global metrics
AI_AGENT_ACTIVE = Gauge('pirc_ai_agents_active', 'Active AI agents')
PI_WALLET_BALANCE = Gauge('pirc_pi_wallet_balance', 'Pi Network wallet balance')

logger = structlog.get_logger("pirc-main")

class PiRCAISuite:
    def __init__(self):
        self.redis = None
        self.security = None
        self.running = False
    
    async def startup(self):
        """Initialize all services"""
        logger.info("🚀 Starting PiRC-AI-SUITE v2.0")
        
        # Start Prometheus metrics server
        start_http_server(9090)
        
        # Initialize Redis & Security
        import redis.asyncio as redis
        self.redis = redis.from_url(settings.redis_url)
        self.security = SecurityMiddleware(self.redis)
        
        # Startup metrics
        MetricsCollector.startup()
        
        # Start FastAPI in background
        config = uvicorn.Config(
            "pirc.api.main:app",
            host=settings.api_host,
            port=settings.api_port,
            log_level="info"
        )
        server = uvicorn.Server(config)
        asyncio.create_task(server.serve())
        
        logger.info("✅ All services started successfully")
    
    async def shutdown(self):
        """Graceful shutdown"""
        logger.info("🛑 Shutting down PiRC-AI-SUITE")
        MetricsCollector.shutdown()
        if self.redis:
            await self.redis.close()
        self.running = False

@asynccontextmanager
async def lifespan():
    suite = PiRCAISuite()
    await suite.startup()
    try:
        yield suite
    finally:
        await suite.shutdown()

async def main():
    """Main entrypoint"""
    async with lifespan():
        # Keep running
        while True:
            await asyncio.sleep(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    except Exception as e:
        logger.error("Fatal error", exc_info=e)
        sys.exit(1)
