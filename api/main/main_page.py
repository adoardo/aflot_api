from beanie import SortDirection
from fastapi import APIRouter, HTTPException
from starlette import status
from models import user_model, company_model, news_model
from models.vacancy import vacancy as VacancyModel
from models.navy import navy as NavyModel
from .schemas import Vacancy, CompanyInfo, ResponseOffers, News, Resume
from schemas.vacancies_company.all_vacancy import VesselSchemas, VacancySchemas, VacanciesResponse, CompanySchemas
from bson import ObjectId

router = APIRouter()

@router.get("/home-page", status_code=status.HTTP_200_OK, summary="Главная страница")
async def get_home_page():
    try:
        news = await news_model.find().sort([("created_at", SortDirection.DESCENDING)]).limit(8).to_list()
        interesting = await news_model.find().sort([("view_count", SortDirection.DESCENDING)]).limit(8).to_list()
        vacancies = await VacancyModel.find().limit(4).to_list()
        resumes = await user_model.find().limit(4).to_list()

        vacancies_companies = []
        vessels_companies = []
        companies_data = []
        for vacancy in vacancies:
            company = await company_model.find_one({'vacancies': vacancy.id})
            vessel = await NavyModel.find_one({"_id": ObjectId(vacancy.vessel)})
            companies_data.append(CompanySchemas(**company.dict()))
            vessels_companies.append(VesselSchemas(**vessel.dict()))
            vacancies_companies.append(VacancySchemas(**vacancy.dict()))

        data = {
            "vacancies2": 0,
            "vacancies": vacancies_companies,
            "vessels": vessels_companies,
            "companies": companies_data,
            "resumes": resumes,
            "news": news,
            "interesting": interesting
        }

        return data

    except HTTPException as e:
        return HTTPException(detail=e, status_code=status.HTTP_400_BAD_REQUEST)
