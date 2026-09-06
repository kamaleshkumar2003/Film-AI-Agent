from fastapi import APIRouter
from app.api.routes.projects import router as projects_router
from app.api.routes.scenes import router as scenes_router
from app.api.routes.jobs import router as jobs_router
from app.api.routes.exports import router as exports_router

api_router = APIRouter()
api_router.include_router(projects_router)
api_router.include_router(scenes_router)
api_router.include_router(jobs_router)
api_router.include_router(exports_router)
