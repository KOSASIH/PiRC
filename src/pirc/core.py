"""PiRC Core - 50Hz Control Loop (2-core-design.md)"""
import asyncio
import time
import structlog
from typing import Callable, Any
from dataclasses import dataclass
from prometheus_client import Histogram, Gauge

logger = structlog.get_logger("pirc.core")

@dataclass
class RobotState:
    battery: float = 1.0
    motors: dict = None
    vision: dict = None
    timestamp: float = 0.0

class PiRCCore:
    LOOP_LATENCY = Histogram('pirc_loop_latency_ms', '50Hz loop time')
    CPU_USAGE = Gauge('pirc_cpu_usage_percent', 'CPU utilization')
    
    def __init__(self):
        self.state = RobotState()
        self.plugins = {}
        self.running = False
        self._loop_rate = 50  # Hz from 2-core-design
        
    def register_plugin(self, name: str, plugin: Callable):
        """Dynamic plugin system"""
        self.plugins[name] = plugin
        logger.info(f"Registered plugin: {name}")
    
    async def sense(self):
        """Sense phase - collect sensors"""
        self.state.timestamp = time.monotonic()
        # GPIO, camera, IMU here
        return self.state
    
    async def plan(self, state: RobotState):
        """Plan phase - AI/TGE decision"""
        # TGE FSM will go here
        return {"motors": {"left": 0, "right": 0}}
    
    async def act(self, commands: dict):
        """Act phase - execute motors/servos"""
        logger.debug(f"Executing: {commands}")
        # GPIO motor control here
    
    async def run(self):
        """Main 50Hz loop - CRITICAL PATH"""
        self.running = True
        logger.info("🚀 PiRC Core starting 50Hz loop")
        
        while self.running:
            loop_start = time.monotonic()
            
            # SENSE → PLAN → ACT (from 2-core-design)
            state = await self.sense()
            commands = await self.plan(state)
            await self.act(commands)
            
            # Run registered plugins
            for name, plugin in self.plugins.items():
                await plugin(state)
            
            # Precise timing
            elapsed = time.monotonic() - loop_start
            await asyncio.sleep(max(0, 1.0/self._loop_rate - elapsed))
            
            self.LOOP_LATENCY.observe(elapsed * 1000)
        
        logger.info("PiRC Core stopped")
