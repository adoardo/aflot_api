from .company_vacancy import router as company_vacancy
from .all_vacancy import router as all_vacancy
from fastapi import APIRouter

vacancy_company_router = APIRouter(
    prefix="/api/v1",
    tags=["Вакансии компаний и все вакансии"]
)

vacancy_company_router.include_router(company_vacancy)
vacancy_company_router.include_router(all_vacancy)
