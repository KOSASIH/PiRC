"""🚀 PiRC v2.1.0 - Super Advanced Pi Robotics + IRC Framework"""

__version__ = "2.1.0"
__author__ = "KOSASIH <kosasihg88@gmail.com>"
__license__ = "MIT"
__description__ = "Chat-Controlled Raspberry Pi Robots - 50Hz Core + YOLOv10 + IRC"

__all__ = [
    "core", "tge", "hardware", "irc", "api", "vision", "metrics", 
    "config", "security", "main", "cli", "plugins"
]

import sys
import asyncio
import logging
import uvloop
from pathlib import Path
from typing import Dict, Any
from dataclasses import dataclass

# Production asyncio setup
uvloop.install()
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

# Enterprise logging (UPGRADED)
import structlog
from structlog.threadlocal import wrap_logger_in_thread_context
from structlog.stdlib import LoggerFactory, BoundLogger
from structlog.processors import (
    TimeStamper, StackInfoRenderer, format_exc_info,
    filter_by_level, add_logger_name, add_log_level,
    JSONRenderer, UnicodeDecoder
)

# PiRC Context
@dataclass(frozen=True)
class PiRCContext:
    """Global application context"""
    version: str = __version__
    loop_rate: float = 50.0  # Hz
    platform: str = "raspberry-pi"
    debug: bool = False

# Global context
CONTEXT = PiRCContext()

def configure_logging(debug: bool = False) -> structlog.stdlib.BoundLogger:
    """Enterprise-grade structured logging"""
    
    # Update context for debug mode
    global CONTEXT
    CONTEXT = PiRCContext(version=__version__, debug=debug)
    
    processors = [
        # Context injection
        wrap_logger_in_thread_context({
            "version": __version__,
            "pid": sys.pid,
            "platform": CONTEXT.platform,
            "loop_rate": CONTEXT.loop_rate,
            "debug": debug
        }),
        
        # Standard processors
        filter_by_level,
        add_logger_name,
        add_log_level,
        TimeStamper(fmt="iso", key="timestamp"),
        StackInfoRenderer(),
        format_exc_info,
        
        # Output format
        JSONRenderer() if not debug else UnicodeDecoder(),
    ]
    
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=LoggerFactory(),
        wrapper_class=BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Python stdlib integration
    logging.basicConfig(
        stream=sys.stdout,
        level=logging.DEBUG if debug else logging.INFO,
        format="%(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    
    logger = structlog.get_logger("pirc")
    logger.info("🚀 PiRC initialized", version=__version__, debug=debug)
    
    return logger

# Auto-configure on import
logging.getLogger("pirc")  # Trigger config
logger = configure_logging(debug=False)

# Metrics integration
try:
    from prometheus_client import REGISTRY, Gauge, Histogram, Counter
    METRICS = {
        "pirc_loop_rate": Gauge("pirc_loop_rate_hz", "Control loop frequency"),
        "pirc_cpu_usage": Gauge("pirc_cpu_usage_percent", "CPU utilization"),
        "pirc_tasks_active": Gauge("pirc_tasks_active", "Active asyncio tasks"),
        "pirc_messages_processed": Counter("pirc_messages_total", "IRC messages processed"),
    }
    logger.info("📊 Prometheus metrics enabled")
except ImportError:
    METRICS = {}
    logger.warning("📊 Prometheus not available")

# Plugin registry
PLUGINS: Dict[str, Any] = {}

def register_plugin(name: str, plugin: Any):
    """Dynamic plugin registration"""
    PLUGINS[name] = plugin
    logger.info(f"🔌 Plugin registered: {name}")

# Graceful shutdown
import atexit
_shutdown_hooks = []

def register_shutdown(hook: Callable):
    """Register shutdown callback"""
    _shutdown_hooks.append(hook)

def _cleanup():
    logger.info("🛑 PiRC shutdown")
    for hook in _shutdown_hooks:
        try:
            asyncio.create_task(hook())
        except:
            pass

atexit.register(_cleanup)

# Export key components
from .core import PiRCCore
from .cli import main  # CLI entrypoint
from .config import PiRCConfig

__pdoc__ = {
    "PLUGINS": False,
    "METRICS": False,
    "CONTEXT": False,
    "configure_logging": False,
}

logger.info("✅ PiRC v2.1.0 fully loaded", plugins=len(PLUGINS))
