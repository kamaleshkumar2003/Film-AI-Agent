from fastapi import APIRouter
from app.api.routes.projects import router as projects_router
from app.api.routes.scenes import router as scenes_router
from app.api.routes.jobs import router as jobs_router
from app.api.routes.exports import router as exports_router
from app.api.routes.cast import router as cast_router
from app.api.routes.crew import router as crew_router
from app.api.routes.locations import router as locations_router
from app.api.routes.schedule import router as schedule_router

api_router = APIRouter()
api_router.include_router(projects_router)
api_router.include_router(scenes_router)
api_router.include_router(jobs_router)
api_router.include_router(exports_router)
api_router.include_router(cast_router)
api_router.include_router(crew_router)
api_router.include_router(locations_router)
api_router.include_router(schedule_router)
