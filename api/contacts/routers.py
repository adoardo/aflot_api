from fastapi import APIRouter
from .get_contact import router
contacts_router = APIRouter(
    prefix="/api/v1",
    tags=["Contacts"],
)

contacts_router.include_router(router)
