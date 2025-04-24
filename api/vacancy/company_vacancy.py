from fastapi import APIRouter, Depends, HTTPException
from models import company_model, auth, user_model, navy
from beanie import PydanticObjectId
from models.vacancy import vacancy as VacancyModel
from starlette import status
from api.auth.config import get_current_user
from typing import Annotated, Optional
from schemas.vacancies_company.user_resume import Resume
from typing import List
from .schemas import (VacancySchemas, VacancyRead, VacanciesResponse, ResponseCount,
                      ResponseNavySchemas, NavySchemas)

router = APIRouter()


@router.get('/create-vacancies', status_code=status.HTTP_200_OK,
            summary="Возвращает судна компании и судна МОРСКОЙ ФЛОТ")
async def get_information_vacancy(current_user: Optional[dict] = Depends(get_current_user)):
    try:

        if current_user is None or current_user['role'] == "Моряк":
            return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Авторизуйтесь")

        company_id = current_user.get("id")
        company_info = await auth.get(company_id)

        if not company_info:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Данная компания не зарегистрирована")

        resume_id = company_info.resumeID

        resume_info = await company_model.get(resume_id)

        if not resume_info:
            return HTTPException(detail="Заполните резюме компании", status_code=status.HTTP_404_NOT_FOUND)

        company_navy = resume_info.vessel

        if not company_navy:
            company_navy = []

        list_company = []

        for nav in company_navy:

            list_company.append(NavySchemas(**nav.dict()))

        navy_site = await navy.find_all().to_list()

        site_list = []

        for nav in navy_site:

            site_list.append(NavySchemas(**nav.dict()))

        return ResponseNavySchemas(companyNavy=list_company, navy=site_list)

    except HTTPException as e:
        return HTTPException(detail=str(e), status_code=status.HTTP_400_BAD_REQUEST)


@router.post("/create-vacancies", response_model=VacancyRead, status_code=status.HTTP_201_CREATED,
             summary="Создать вакансию")
async def create_vacancies_by_company(jobs_create: VacancySchemas,
                                      current_user: Annotated[dict, Depends(get_current_user)]):
    try:
        if current_user is None or current_user['role'] == "Моряк":
            return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Авторизуйтесь")

        company_id = current_user.get("id")
        company_info = await auth.get(company_id)

        if not company_info:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Данная компания не зарегистрирована")

        company = await company_model.get(company_info.resumeID)
        new_vacancy = VacancyModel(**jobs_create.dict())

        await new_vacancy.create()

        if not company.vacancies:
            company.vacancies = []

        company.vacancies.append(new_vacancy.id)
        await company.save()

        return new_vacancy
    except HTTPException as e:
        raise HTTPException(detail=str(e), status_code=status.HTTP_400_BAD_REQUEST)


@router.get("/vacancies", status_code=status.HTTP_200_OK, response_model=List[VacanciesResponse],
            summary="Просмотреть вакансии для компании")
async def get_company_vacancies(current_user: Annotated[dict, Depends(get_current_user)]):
    try:
        company_id = current_user.get("id")
        company_info = await auth.get(company_id)

        if not company_info:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Данная компания не зарегистрирована")

        company = await company_model.get(company_info.resumeID)
        vacancies = company.vacancies

        vacancies_info = []

        for vacancy in vacancies:
            vacancies_data = await VacancyModel.get(vacancy)
            if vacancies_data.status == 'активная вакансия':
                response_count = len(vacancies_data.responses) if vacancies_data.responses else 0
                response = VacanciesResponse(
                    vacancies=VacancyModel(**dict(vacancies_data)),
                    responseCount=ResponseCount(responseCount=response_count),
                )
                vacancies_info.append(response)
            else:
                pass

        return vacancies_info
    except HTTPException as e:

        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e)


@router.get('/vacancies/{vacancy_id}/response', status_code=status.HTTP_200_OK, response_model=List[Resume],
            summary="Просмотреть отклики на данную вакансию")
async def response_vacancy_id(vacancy_id: PydanticObjectId,
                              current_user: Annotated[dict, Depends(get_current_user)]):
    try:

        company_id = current_user.get("id")
        company_info = await auth.get(company_id)

        if not company_info:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Данная компания не зарегистрирована")

        vacancy = await VacancyModel.get(vacancy_id)

        if not vacancy:
            raise HTTPException(detail='Vacancy not found', status_code=status.HTTP_404_NOT_FOUND)

        responses = vacancy.responses

        resume_list = []
        for response in responses:
            resume = await user_model.get(response)

            resume_list.append(resume)

        return resume_list
    except HTTPException as e:

        return e


@router.get('/vacancies/{vacancy_id}/job-offers', status_code=status.HTTP_200_OK,
            summary="Просмотреть отправленные предложения по данной вакансии")
async def job_offers_vacancy_id(vacancy_id: PydanticObjectId,
                                current_user: Annotated[dict, Depends(get_current_user)]):
    try:

        company_id = current_user.get("id")
        company_info = await auth.get(company_id)

        if not company_info:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Данная компания не зарегистрирована")

        company = await company_model.get(company_info.resumeID)

        job_offers = company.job_offers

        job_offers_info = []

        for job_offer in job_offers:
            job_offers_data = await user_model.get(job_offer)
            job_offers_data.append(job_offer)

        return job_offers_info
    except HTTPException as e:

        return HTTPException(detail=str(e), status_code=status.HTTP_400_BAD_REQUEST)


@router.get('/vacancies/{vacancy_id}/ready-to-work', status_code=status.HTTP_200_OK,
            summary="Готовые к работе по данной вакансии")
async def response_vacancy_id(vacancy_id: PydanticObjectId,
                              current_user: Annotated[dict, Depends(get_current_user)]):
    try:

        company_id = current_user.get("id")
        company_info = await auth.get(company_id)

        if not company_info:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Данная компания не зарегистрирована")

        company = await company_model.get(company_info.resumeID)

    except HTTPException as e:

        return HTTPException(detail=str(e), status_code=status.HTTP_400_BAD_REQUEST)


@router.get('/drafts', status_code=status.HTTP_200_OK, summary="Черновики")
async def get_drafts_vacancy(current_user: Annotated[dict, Depends(get_current_user)]):
    try:

        pass


    except HTTPException as e:

        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e)


@router.get('/irrelevant-vacancies', status_code=status.HTTP_200_OK, summary="Неактуальные вакансии")
async def get_irrelevant_vacancy(current_user: Annotated[dict, Depends(get_current_user)]):
    try:

        company_id = current_user.get("id")
        company_info = await auth.get(company_id)

        if not company_info:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Данная компания не зарегистрирована")

        company = await company_model.get(company_info.resumeID)
        vacancies = company.vacancies

        vacancies_info = []

        for vacancy in vacancies:
            vacancies_data = await VacancyModel.get(vacancy.id)

            if vacancies_data.status == 'Неактуальная вакансия':
                vacancies_info.append(vacancies_data)

        return vacancies_info
    except HTTPException as e:

        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e)


@router.put('/irrelevant-vacancies/{vacancy_id}/active', status_code=status.HTTP_201_CREATED,
            summary="Сделать актуальной вакансию")
async def active_irrelevant_vacancy(current_user: Annotated[dict, Depends(get_current_user)],
                                    vacancy_id: PydanticObjectId):
    try:

        company_id = current_user.get("id")
        company_info = await auth.get(company_id)

        if not company_info:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Данная компания не зарегистрирована")

        vacancy = await VacancyModel.get(vacancy_id)

        await vacancy.update({"$set": {"status": "активная вакансия"}})

        return vacancy
    except HTTPException as e:

        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e)


@router.delete('/irrelevant-vacancies/{vacancy_id}/delete', status_code=status.HTTP_200_OK,
               summary="Удалить вакансию")
async def delete_irrelevant_vacancy(current_user: Annotated[dict, Depends(get_current_user)],
                                    vacancy_id: PydanticObjectId):
    try:
        company_id = current_user.get("id")
        company_info = await auth.get(company_id)

        if not company_info:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Данная компания не зарегистрирована")

        company = await company_model.get(company_info.resumeID)

        await company_model.update(company, {"$pull": {"vacancies": {"id": vacancy_id}}})

        vacancy = await VacancyModel.get(vacancy_id)
        await vacancy.delete()

        return vacancy

    except HTTPException as e:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e)


@router.put('/vacancies/{vacancy_id}/close', status_code=status.HTTP_201_CREATED,
            summary="Закрыть вакансию")
async def close_vacancy(current_user: Annotated[dict, Depends(get_current_user)], vacancy_id: PydanticObjectId):
    try:
        company_id = current_user.get("id")
        company_info = await auth.get(company_id)

        if not company_info:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Данная компания не зарегистрирована")

        vacancy = await VacancyModel.get(vacancy_id)

        await vacancy.update({"$set": {"status": "Неактуальная вакансия"}})

        return vacancy

    except HTTPException as e:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e)


@router.get("/vacancies/{vacancy_id}", status_code=status.HTTP_200_OK,
            summary="Подробнее о вакансии")
async def get_vacancies_by_company(current_user: Annotated[dict, Depends(get_current_user)],
                                   vacancy_id: PydanticObjectId):
    try:

        company_id = current_user.get("id")
        company_info = await auth.get(company_id)

        if not company_info:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Данная компания не зарегистрирована")

        vacancy = await VacancyModel.get(vacancy_id)

        if not vacancy:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Данная вакансия не найдена")

        return vacancy

    except HTTPException as e:

        raise HTTPException(detail=str(e), status_code=status.HTTP_400_BAD_REQUEST)


@router.put("/vacancies/{vacancy_id}", response_model=VacancyRead, status_code=status.HTTP_201_CREATED,
            summary="Редактировать вакансию")
async def update_vacancies_by_company(request: VacancyModel, vacancy_id: PydanticObjectId,
                                      current_user: Optional[dict] = Depends(get_current_user)):
    try:

        company_id = current_user.get("id")
        company_info = await auth.get(company_id)

        if not company_info:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Данная компания не зарегистрирована")

        request = {k: v for k, v in request.dict().items() if v is not None}

        update_query = {"$set": {
            field: value for field, value in request.items()
        }}

        job = await VacancyModel.get(vacancy_id)

        if not job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Данная вакансия не найдена")

        company = await company_model.get(company_id)

        if not company:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Данная компания не найдена")

        await job.update(update_query)

        return job
    except HTTPException as e:

        raise HTTPException(detail=str(e), status_code=status.HTTP_400_BAD_REQUEST)
