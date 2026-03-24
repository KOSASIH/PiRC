# src/pirc/core/scheduler.py
"""Static Priority Scheduler - 20μs precision"""
import uvloop
import trio
from typing import Dict, Any
from dataclasses import dataclass
import time
from prometheus_client import Histogram, Gauge

uvloop.install()

@dataclass
class TaskSlice:
    name: str
    cpu_share: float  # 0.0-1.0
    max_us: int
    priority: int

class PiRCScheduler:
    TASK_LATENCY = Histogram('pirc_task_latency_us', 'Task execution time')
    CPU_UTIL = Gauge('pirc_cpu_utilization', 'CPU usage by task')
    
    def __init__(self):
        self.tasks: Dict[str, TaskSlice] = {
            'core': TaskSlice('core', 0.40, 8000, 1),
            'vision': TaskSlice('vision', 0.30, 6000, 2),
            'ai': TaskSlice('ai', 0.20, 4000, 3),
            'actuators': TaskSlice('actuators', 0.08, 1600, 4),
        }
        self.monotonic_ns = time.monotonic_ns
    
    async def tick(self):
        """50Hz master tick - 20ms frame"""
        frame_start = self.monotonic_ns()
        
        for task_name, slice_ in self.tasks.items():
            task_start = self.monotonic_ns()
            await self._execute_task(task_name)
            latency_us = (self.monotonic_ns() - task_start) // 1000
            self.TASK_LATENCY.labels(task=task_name).observe(latency_us)
            
            if latency_us > slice_.max_us:
                print(f"🚨 {task_name} OVERRUN: {latency_us}μs")
        
        frame_us = (self.monotonic_ns() - frame_start) // 1000
        assert frame_us < 20000, f"Frame overrun: {frame_us}μs"
