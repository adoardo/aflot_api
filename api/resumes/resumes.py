import math
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Annotated, List
from datetime import date, datetime
from api.auth.config import get_current_user
from api.vacancy.schemas import VacancySchemas
from models import user_model, auth, company_model, BlackList
from models.vacancy import vacancy as VacancyModel
from starlette import status
from beanie import PydanticObjectId
from schemas.resumes.user_resume import UserResumeResponse, PostAJobsRequest, UserResume
from schemas.auth.auth import BlackListComment

router = APIRouter()


@router.get("/resumes", summary="Возвращает все резюме моряков")
async def get_all_resumes(page: int = 1, page_size: int = 6):
    try:

        skip = (page - 1) * page_size
        limit = page_size

        total_count = await user_model.find().count()
        total_pages = math.ceil(total_count / page_size)

        resumes = await user_model.find().skip(skip).limit(limit).to_list()

        resume_list = []
        for resume in resumes:
            resume_list.append(UserResume(**resume.dict()))

        return {
            "current_page": page,
            "resumes": resumes,
            "total_pages": total_pages
        }

    except HTTPException as e:

        return HTTPException(detail=e, status_code=status.HTTP_400_BAD_REQUEST)


@router.post("/resumes/search", summary="Поиск резюме")
async def search_resumes(
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

        total_resume = await user_model.find(filter_query).count()
        total_pages = math.ceil(total_resume / page_size)
        resumes_db = await user_model.find(filter_query).skip((page - 1) * page_size).limit(page_size).to_list()

        resumes_list = []
        for resume in resumes_db:
            resumes_list.append(UserResume(**resume.dict()))

        return UserResumeResponse(current_page=page, vacancies=resumes_list, total_page=total_pages)

    except HTTPException as e:

        return HTTPException(detail=e, status_code=status.HTTP_400_BAD_REQUEST)


@router.get("/resumes/{sailor_id}", response_model=user_model, summary="Возвращает резюме по ID")
async def get_user_vacancy(sailor_id: PydanticObjectId):
    try:

        user_vacancy = await user_model.get(sailor_id)

        if not user_vacancy:
            raise HTTPException(detail="User not found", status_code=status.HTTP_404_NOT_FOUND)

        return user_vacancy

    except HTTPException as e:

        return HTTPException(detail=e, status_code=status.HTTP_400_BAD_REQUEST)

@router.get("/sailorinfo/{sailor_id}", summary="Возвращает анкету по ID")
async def get_user_vacancy(sailor_id: PydanticObjectId):
    try:

        sailorinfo = await user_model.get(sailor_id)

        if not sailorinfo:
            raise HTTPException(detail="User not found", status_code=status.HTTP_404_NOT_FOUND)

        return sailorinfo

    except HTTPException as e:

        return HTTPException(detail=e, status_code=status.HTTP_400_BAD_REQUEST)

@router.get("/resumes/{sailor_id}/post-a-job", status_code=status.HTTP_200_OK, response_model=List[VacancySchemas],
            summary="Предлажение вакансии от компании. Возвращает массив вакансий от компании")
async def post_a_job_get(sailor_id: PydanticObjectId, current_user: Annotated[dict, Depends(get_current_user)]):
    try:

        if current_user is None or current_user['role'] == "Моряк":
            raise HTTPException(detail="Для начало авторизуйтесь как компания", status_code=status.HTTP_204_NO_CONTENT)

        company_id = current_user.get('id')
        company_info = await auth.get(company_id)

        if not company_info:
            raise HTTPException(detail="Company not found", status_code=status.HTTP_404_NOT_FOUND)

        company = await company_model.get(company_info.resumeID)

        vacancy_list = company.vacancies

        response_list = []

        for vacancy in vacancy_list:
            jobs = await VacancyModel.get(vacancy)

            response_list.append(jobs)

        return response_list

    except HTTPException as e:

        return HTTPException(detail=e, status_code=status.HTTP_400_BAD_REQUEST)


@router.post("/resumes/{sailor_id}/post-a-job", summary="Отправляет вакансию для моряка",
             status_code=status.HTTP_200_OK)
async def post_a_job_post(sailor_id: PydanticObjectId, request: PostAJobsRequest,
                          current_user: Annotated[dict, Depends(get_current_user)]):
    try:

        if current_user is None or current_user['role'] == "Моряк":
            raise HTTPException(detail="Для начало авторизуйтесь как компания", status_code=status.HTTP_404_NOT_FOUND)

        company_id = current_user.get('id')
        company_info = await auth.get(company_id)

        if not company_info:
            raise HTTPException(detail="Company not found", status_code=status.HTTP_404_NOT_FOUND)

        offer = await user_model.get(sailor_id)

        if not offer.offers:
            offer.offers = []

        offer.offers.append(request.id)

        await offer.save()

        return "Вакансия успешно отправлена"

    except HTTPException as e:

        return HTTPException(detail=e, status_code=status.HTTP_400_BAD_REQUEST)



#Favorite items and BlackList items

@router.post("/resumes/favorite/add/{sailor_id}", status_code=status.HTTP_201_CREATED,
             summary="Добавить моряка в избранные")
async def add_user_to_favorite(sailor_id: PydanticObjectId, current_user: Annotated[dict, Depends(get_current_user)]):
    try:
        company_id = current_user.get('id')
        company_info = await auth.get(company_id)
        if not company_info:
            raise HTTPException(detail="Company not found", status_code=status.HTTP_404_NOT_FOUND)

        company = await company_model.get(company_info.resumeID)
        if not company.favorites_resume:
            company.favorites_resume = []

        if sailor_id not in company.favorites_resume:
            company.favorites_resume.append(sailor_id)

        await company.save()

        return { 1 }

    except HTTPException as e:
        return HTTPException(detail=e, status_code=status.HTTP_400_BAD_REQUEST)


@router.post('/resumes/blacklist/add/{sailor_id}', status_code=status.HTTP_201_CREATED,
             summary="Добавить моряка в черный список")
async def add_blacklist(sailor_id: PydanticObjectId, current_user: Annotated[dict, Depends(get_current_user)], blc: BlackListComment):
    try:
        company_id = current_user.get('id')
        company_info = await auth.get(company_id)
        if not company_info:
            raise HTTPException(detail="Company not found", status_code=status.HTTP_404_NOT_FOUND)

        company = await company_model.get(company_info.resumeID)

        if not company.black_list:
            company.black_list = []

        exist = False
        for row in company.black_list:
            if sailor_id == row.sailor_id:
                exist = True

        if not exist:
            company.black_list.append(BlackList(**blc.dict()))

        await company.save()

        return { 1 }

    except HTTPException as e:

        return HTTPException(detail=e, status_code=status.HTTP_400_BAD_REQUEST)


@router.post("/resumes/favorite/remove/{sailor_id}", status_code=status.HTTP_201_CREATED,
             summary="Удалить моряка из изранных")
async def remove_user_to_favorite(sailor_id: PydanticObjectId, current_user: Annotated[dict, Depends(get_current_user)]):
    try:
        company_id = current_user.get('id')
        company_info = await auth.get(company_id)
        if not company_info:
            raise HTTPException(detail="Company not found", status_code=status.HTTP_404_NOT_FOUND)

        company = await company_model.get(company_info.resumeID)

        if not company.favorites_resume:
            company.favorites_resume = []

        company.favorites_resume.remove(sailor_id)

        await company.save()

        return { 1 }

    except HTTPException as e:
        return HTTPException(detail=e, status_code=status.HTTP_400_BAD_REQUEST)


@router.post('/resumes/blacklist/remove/{sailor_id}', status_code=status.HTTP_201_CREATED,
             summary="Удалить моряка из черного списка")
async def remove_blacklist(sailor_id: PydanticObjectId, current_user: Annotated[dict, Depends(get_current_user)]):
    try:
        company_id = current_user.get('id')
        company_info = await auth.get(company_id)
        if not company_info:
            raise HTTPException(detail="Company not found", status_code=status.HTTP_404_NOT_FOUND)

        company = await company_model.get(company_info.resumeID)

        if not company.black_list:
            company.black_list = []

        black_list = []
        for row in company.black_list:
            if sailor_id != row.sailor_id:
                black_list.append(row)

        company.black_list = black_list

        await company.save()

        return { 1 }

    except HTTPException as e:

        return HTTPException(detail=e, status_code=status.HTTP_400_BAD_REQUEST)

@router.get("/bflist", status_code=status.HTTP_200_OK, summary="Возвращает списки избранных моряков и моряков черного списка компании.")
async def get_bflist(current_user: Annotated[dict, Depends(get_current_user)]):
    try:
        company_id = current_user.get('id')
        company_info = await auth.get(company_id)
        if not company_info:
            raise HTTPException(detail="Company not found", status_code=status.HTTP_404_NOT_FOUND)

        company = await company_model.get(company_info.resumeID)

        black_list = []
        for row in company.black_list:
            black_list.append(row.sailor_id)

        favorite_list = company.favorites_resume

        filter_query = {}
        filter_query["_id"] = {"$in": company.favorites_resume}
        favorites = await user_model.find(filter_query).to_list()

        filter_query["_id"] = {"$in": black_list}
        black_lists = await user_model.find(filter_query).to_list()

        return {
            "favorites": favorites,
            "black_list": black_lists,
            "blc": company.black_list
        }

    except HTTPException as e:

        return HTTPException(detail=e, status_code=status.HTTP_400_BAD_REQUEST)

