from fastapi import APIRouter
from .get_history import router as get_history_router
history_router = APIRouter()


history_router.include_router(get_history_router)
