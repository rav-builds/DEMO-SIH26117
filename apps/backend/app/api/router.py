from fastapi import APIRouter

from app.api.routes.health import router as health_router
from app.api.routes.knowledge import router as knowledge_router
from app.api.routes.security import router as security_router
from app.api.routes.tasks import router as tasks_router

api_router = APIRouter()

api_router.include_router(health_router, tags=["health"])
api_router.include_router(tasks_router, tags=["tasks"])
api_router.include_router(knowledge_router, tags=["knowledge"])
api_router.include_router(security_router, tags=["security"])
