from fastapi import APIRouter, HTTPException, Depends, Query
import math
from starlette import status
from beanie import PydanticObjectId
from models import company_model, auth, user_model
from models.register import FavoritesVacancies, FavoritesCompany
from models import ship as ShipModel
from typing import Optional
from api.auth.config import get_current_user
from starlette.responses import JSONResponse
from datetime import date
from schemas.vacancies_company.all_vacancy import VacanciesResponse, VacanciesCompany
from schemas.vacancies_company.search_vacancy import SearchVacanciesResponse, Vacancy

router = APIRouter()


@router.get("/all-vacancies", status_code=status.HTTP_200_OK, response_model=VacanciesResponse,
            summary="Все вакансии компаний")
async def get_all_vacancies(page: int = 1, page_size: int = 7):
    try:

        skip = (page - 1) * page_size
        limit = page_size

        total_vacancies = await ShipModel.find().count()
        total_page = math.ceil(total_vacancies / page_size)
        vacancies = await ShipModel.find().skip(skip).limit(limit).to_list()

        vacancies_companies = []
        for vacancy in vacancies:
            vacancies_companies.append(VacanciesCompany(**vacancy.dict()))

        data = VacanciesResponse(
            current_page=page,
            total_pages=total_vacancies,
            vacancies=vacancies_companies,
        )

        return data

    except HTTPException as e:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e)


@router.get("/all-vacancies/search", status_code=status.HTTP_200_OK, response_model=SearchVacanciesResponse,
            summary="Поиск вакансий компаний")
async def search_vacancies(
        salary: str = Query(None),
        ship_type: str = Query(None),
        position: str = Query(None),
        date_of_departure: date = Query(None),
        contract_duration: str = Query(None),
        page: int = 1, page_size: int = 7):
    try:
        filter_query = {}
        if salary:
            filter_query["salary"] = salary
        if ship_type:
            filter_query["ship_type"] = ship_type
        if position:
            filter_query["position"] = {"$regex": position, "$options": "i"}
        if date_of_departure:
            filter_query["date_of_departure"] = date_of_departure
        if contract_duration:
            filter_query["contract_duration"] = contract_duration

        total_vacancies = await ShipModel.find(filter_query).count()
        total_pages = math.ceil(total_vacancies / page_size)
        vacancies_db = await ShipModel.find(filter_query).skip((page - 1) * page_size).limit(page_size).to_list()

        vacancies_companies = []
        for vacancy in vacancies_db:
            vacancies_companies.append(Vacancy(**vacancy.dict()))

        return SearchVacanciesResponse(vacancies=vacancies_companies, total_pages=total_pages, current_page=page)

    except Exception as e:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/all-vacancies/{vacancies_id}", status_code=status.HTTP_200_OK, summary="Подробнее о вакансии")
async def get_vacancies_id(vacancies_id: PydanticObjectId):
    try:

        data = []

        vacancies = await ShipModel.find_one({"_id": vacancies_id})

        if not vacancies:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Данная вакансия не найдена")

        data.append(vacancies)
        company = await company_model.find_one({'vacancies': vacancies_id})

        if not company:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Вакансия по данной компании не доступна")

        company_info = {
            "id": str(PydanticObjectId(company.id)),
            "company_name": company.company_name,

        }
        data.append(company_info)

        return data

    except HTTPException as e:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e)


@router.post('/all-vacancies/{vacancies_id}/respond', summary="Отправить отклик на вакансию")
async def respond_vacancy(vacancies_id: PydanticObjectId, current_user: Optional[dict] = Depends(get_current_user)):
    try:

        if current_user is None or current_user['role'] == 'Компания':
            return HTTPException(detail="Авторизуйтесь", status_code=status.HTTP_200_OK)

        user_id = current_user.get("id")

        user_info = await auth.get(user_id)

        if not user_info:
            raise HTTPException(detail="User not found", status_code=status.HTTP_401_UNAUTHORIZED)

        resume_id = user_info.resumeID

        vacancy_info = await ShipModel.get(vacancies_id)

        if not vacancy_info:
            raise HTTPException(detail="Vacancy not found", status_code=status.HTTP_404_NOT_FOUND)

        if not vacancy_info.responses:
            vacancy_info.responses = []

        vacancy_info.responses.append(resume_id)

        await vacancy_info.save()

        return JSONResponse(content="Отклик на вакансию отправлен", status_code=status.HTTP_200_OK)

    except HTTPException as e:

        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e)


@router.post("/all-vacancies/{vacancies_id}/favorite", summary="Добавить вакакнсию в Избранные")
async def add_vacancy_to_favorite(vacancies_id: PydanticObjectId,
                                  current_user: Optional[dict] = Depends(get_current_user)):
    try:

        if current_user is None or current_user['role'] == 'Компания':
            return HTTPException(detail="Авторизуйтесь", status_code=status.HTTP_200_OK)

        user_id = current_user.get('id')

        if not user_id:
            raise HTTPException(detail='User not found', status_code=status.HTTP_404_NOT_FOUND)

        resume_id = await auth.get(user_id)

        if not resume_id:
            raise HTTPException(detail='Resume not found', status_code=status.HTTP_404_NOT_FOUND)

        resume = await user_model.get(resume_id.resumeID)

        new_favorite = FavoritesVacancies(id=vacancies_id)

        if not resume.favorites_vacancies:
            resume.favorites_vacancies = []

        resume.favorites_vacancies.append(new_favorite)

        await resume.save()

        return {"message": f"{vacancies_id} - added to favorites"}

    except HTTPException as e:

        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e)


@router.post("/all-vacancies/{vacancies_id}/favorite/company/{company_id}", summary="Добавить компанию в Избранные")
async def add_company_to_favorite(vacancies_id: PydanticObjectId, company_id: PydanticObjectId,
                                  current_user: Optional[dict] = Depends(get_current_user)):
    try:

        if current_user is None or current_user['role'] == 'Компания':
            return HTTPException(detail="Авторизуйтесь", status_code=status.HTTP_200_OK)

        user_id = current_user.get('id')

        if not user_id:
            raise HTTPException(detail='User not found', status_code=status.HTTP_404_NOT_FOUND)

        user = await auth.get(user_id)

        resume = await user_model.get(user.resumeID)

        new_favorite_company = FavoritesCompany(id=company_id)

        if not resume.favorites_company:
            resume.favorites_company = []

        for i in resume.favorites_company:

            if i.id == company_id:
                return HTTPException(detail="Данная компания уже у вас в избранных", status_code=status.HTTP_200_OK)

        resume.favorites_company.append(new_favorite_company)

        await resume.save()

        return {"message": f"{company_id} - added to favorites"}

    except HTTPException as e:

        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e)


@router.get("/all-vacancies/{vacancies_id}/all-vacancies-company/{company_id}", status_code=status.HTTP_200_OK,
            summary="Просмотреть все вакансии данной компании")
async def get_all_vacancies_company(vacancies_id: PydanticObjectId, company_id: PydanticObjectId):
    try:

        company = await company_model.get(company_id)

        if not company:
            raise HTTPException(detail='Company not found', status_code=status.HTTP_404_NOT_FOUND)

        company_all_vacancy = company.vacancies if company.vacancies else []

        if not company_all_vacancy:
            return company_all_vacancy

        data = []
        for vacancy in company_all_vacancy:
            job = await ShipModel.get(vacancy)

            data.append(job)

        return data

    except HTTPException as e:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e)
