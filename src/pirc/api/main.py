"""🚀 FastAPI Admin Dashboard + Metrics API"""

from contextlib import asynccontextmanager
from typing import List, Dict, Any

import uvicorn
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import prometheus_client
from prometheus_client import Counter, Histogram, Gauge
from pydantic import BaseModel

from ..config import settings
from ..security import SecurityMiddleware
from ..metrics import MetricsCollector
import structlog

# Prometheus Metrics
REQUEST_COUNT = Counter('pirc_requests_total', 'Total requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('pirc_request_duration_seconds', 'Request duration')
ACTIVE_USERS = Gauge('pirc_active_users', 'Active users')
BANNED_USERS = Gauge('pirc_banned_users_total', 'Total banned users')

logger = structlog.get_logger("api")

class HealthCheck(BaseModel):
    status: str = "healthy"
    version: str = "2.0.0"
    uptime: float = 0.0

@asynccontextmanager
async def lifespan(app: FastAPI):
    """App lifespan manager"""
    # Startup
    logger.info("🚀 Starting PiRC API v2.0")
    MetricsCollector.startup()
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down PiRC API")
    MetricsCollector.shutdown()

app = FastAPI(
    title="PiRC Admin Dashboard",
    description="Super Advanced IRC Client Management",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="src/pirc/api/static"), name="static")
templates = Jinja2Templates(directory="src/pirc/api/templates")

# Dependency
async def get_security() -> SecurityMiddleware:
    from ..main import security_middleware
    return security_middleware

@app.middleware("http")
async def metrics_middleware(request, call_next):
    """Prometheus metrics middleware"""
    start_time = prometheus_client.platform.monotonic_time()
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status="200"
    ).inc()
    
    response = await call_next(request)
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=str(response.status_code)
    ).inc()
    
    duration = prometheus_client.platform.monotonic_time() - start_time
    REQUEST_DURATION.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)
    
    return response

@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint"""
    return HealthCheck()

@app.get("/metrics")
async def prometheus_metrics():
    """Prometheus metrics endpoint"""
    return prometheus_client.generate_latest()

@app.get("/dashboard")
async def dashboard(request: Any):
    """Admin dashboard"""
    stats = await MetricsCollector.get_stats()
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "stats": stats}
    )

@app.get("/api/stats")
async def api_stats():
    """API stats endpoint"""
    stats = {
        "active_users": int(ACTIVE_USERS._value.get()),
        "banned_users": int(BANNED_USERS._value.get()),
        "requests_total": sum(REQUEST_COUNT._metrics.values()),
        "uptime": MetricsCollector.uptime()
    }
    return stats

@app.post("/api/ban/{user_id}")
async def ban_user(user_id: str, background_tasks: BackgroundTasks, security: SecurityMiddleware = Depends(get_security)):
    """Ban user via API"""
    background_tasks.add_task(security.rate_limiter.ban_user, user_id)
    BANNED_USERS.inc()
    return {"status": "banned", "user_id": user_id}

@app.get("/api/users/active")
async def active_users() -> List[str]:
    """Get active users"""
    # Implementation in metrics collector
    return await MetricsCollector.get_active_users()

if __name__ == "__main__":
    uvicorn.run(
        "pirc.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        log_level="info",
        reload=False
    )
