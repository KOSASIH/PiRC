"""🚀 PiRC v2.0 - Super Advanced IRC Client"""

__version__ = "2.0.0"
__all__ = ["client", "config", "metrics", "security", "main"]

import logging
import sys
from pathlib import Path

# Setup structured logging
import structlog

structlog.configure(
    processors=[
        structlog.threadlocal.wrap_logger_in_thread_context({"version": __version__}),
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logging.basicConfig(
    stream=sys.stdout,
    format="%(message)s",
    level=logging.INFO,
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = structlog.get_logger("pirc")
