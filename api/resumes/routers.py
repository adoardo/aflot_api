from fastapi import APIRouter
from .resumes import router

resumes_router = APIRouter(
    prefix="/api/v1",
    tags=["Резюме моряка"],
)


resumes_router.include_router(router)

