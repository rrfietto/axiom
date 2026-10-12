from fastapi import APIRouter

from app.api.artworks import router as artworks_router
from app.api.health import router as health_router
from app.api.presets import router as presets_router
from app.api.render import router as render_router

api_router = APIRouter()
api_router.include_router(artworks_router)
api_router.include_router(health_router)
api_router.include_router(presets_router)
api_router.include_router(render_router)
