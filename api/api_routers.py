from fastapi import APIRouter
from .auth.routers import auth_router
from .news.routers import news_router
from .resumes.routers import resumes_router
from .navy.routers import company_router
from .vacancy.routers import vacancy_company_router
from .company_profile.routers import profile_router
from .tariffs.routers import tariffs_router
from .favorites.routers import favorite_router
from .contacts.routers import contacts_router
from .sailor_profile.routers import sailor_profile_router
from .real_history.routers import history_router
from .main.routers import main_router
from .settings.routers import settings_router
from .balance_and_history_payment.routers import balance_router
from .photo_and_logo.routers import download_router
from .offers.router import offers_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(news_router)
api_router.include_router(resumes_router)
api_router.include_router(company_router)
api_router.include_router(vacancy_company_router)
api_router.include_router(profile_router)
api_router.include_router(tariffs_router)
api_router.include_router(favorite_router)
api_router.include_router(contacts_router)
api_router.include_router(sailor_profile_router)
api_router.include_router(history_router)
api_router.include_router(main_router)
api_router.include_router(settings_router)
api_router.include_router(balance_router)
api_router.include_router(download_router)
api_router.include_router(offers_router)
