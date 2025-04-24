from fastapi import APIRouter, HTTPException, Depends, Query
import math
from starlette import status
from beanie import PydanticObjectId
from models import company_model, auth, user_model
from models.register import FavoritesVacancies, FavoritesCompany
from models.vacancy import vacancy as VacancyModel
from models.navy import navy as NavyModel
from typing import Annotated, Optional
from api.auth.config import get_current_user
from starlette.responses import JSONResponse
from datetime import date, datetime
from schemas.vacancies_company.all_vacancy import VesselSchemas, VacancySchemas, VacanciesResponse, CompanySchemas
from schemas.vacancies_company.search_vacancy import SearchVacanciesResponse, SearchVacancy
from bson import ObjectId

router = APIRouter()

@router.post("/all-vacancies/create", status_code=status.HTTP_200_OK,
            summary="Создать вакансию")
async def create_vacancy(vacancy_data: VacancySchemas, current_user: Annotated[dict, Depends(get_current_user)]):
    try:

        if current_user is None or current_user['role'] != "Компания":
            return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Авторизуйтесь")

        company_id = current_user.get("id")
        company_info = await auth.get(company_id)

        if not company_info:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Данная компания не зарегистрирована")

        new_vacancy = VacancyModel(**vacancy_data.dict())
        await new_vacancy.create()

        company = await company_model.get(company_info.resumeID)

        if not company.vacancies:
            company.vacancies = []

        if not company.vessel:
            company.vessel = []

        vacancies_list = company.vacancies
        vacancies_list.append(new_vacancy.id);

        await company.update({"$set": {"vacancies": vacancies_list}})

        if vacancy_data.append_company:
            vessel_list = company.vessel
            vid = ObjectId(vacancy_data.vessel)

            if vid not in vessel_list:
                vessel_list.append(vid)

            await company.update({"$set": {"vessel": vessel_list}})

        await company.save()

        return new_vacancy

    except HTTPException as e:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e)


@router.get("/all-vacancies", status_code=status.HTTP_200_OK, summary="Все вакансии")
async def get_all_vacancies(salary_from: int = Query(None),salary_to: int = Query(None),positions: str = Query(None),ships: str = Query(None), contract_duration: str = Query(None), contract_duration_from: str = Query(None), contract_duration_to: str = Query(None), search: str = Query(None), page: int = 1, page_size: int = 7):
    try:
        filter_query = {}
        if salary_from and salary_to:
            if (salary_from > salary_to):
                salary_from = salary_to
            filter_query["salary_from"] = {"$gte": salary_from}
            filter_query["salary_to"] = {"$lte": salary_to}
        else:
            if salary_from:
                filter_query["salary_from"] = {"$gte": salary_from}
            if salary_to:
                filter_query["salary_to"] = {"$lte": salary_to}
        if positions:
            positions_arr = positions.split(',')
            filter_query["position"] = {"$in": positions_arr}
        if search:
            filter_query["position"] = {"$regex": search, "$options": "i"}
        filter_query["is_publish"] = {"$eq": True}
        filter_query["is_active"] = {"$eq": True}

        skip = (page - 1) * page_size
        limit = page_size

        total_vacancies = await VacancyModel.find(filter_query).count()
        total_page = math.ceil(total_vacancies / page_size)
        vacancies = await VacancyModel.find(filter_query).skip(skip).limit(limit).to_list()


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
            "current_page": page,
            "total_pages": total_page,
            "vacancies": vacancies_companies,
            "vessels": vessels_companies,
            "companies": companies_data,
            "total_vacancies": total_vacancies
        }

        return data

    except HTTPException as e:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e)


@router.get("/all-vacancies/company/{company_id}", summary="Все активные вакансии компании")
async def get_all_vacancies_company(company_id: str, page: int = 1, page_size: int = 7):
    try:
        company_data = await company_model.find_one({"_id": ObjectId(company_id)})
        #company_data = await company_model.find_one({'_id': company_id})
        #company_data = CompanySchemas(**company_obj_data.dict())

        filter_query = {}
        filter_query["is_publish"] = {"$eq": True}
        filter_query["is_active"] = {"$eq": True}
        filter_query["_id"] = {"$in": company_data.vacancies}

        skip = (page - 1) * page_size
        limit = page_size

        total_vacancies = await VacancyModel.find(filter_query).count()
        total_page = math.ceil(total_vacancies / page_size)
        vacancies = await VacancyModel.find(filter_query).skip(skip).limit(limit).to_list()

        vacancies_company = []
        vessels_company = []
        for vacancy in vacancies:
            vessel = await NavyModel.find_one({"_id": ObjectId(vacancy.vessel)})
            vessels_company.append(VesselSchemas(**vessel.dict()))
            vacancies_company.append(VacancySchemas(**vacancy.dict()))

        data = {
            "current_page": page,
            "total_pages": total_page,
            "vacancies": vacancies_company,
            "vessels": vessels_company,
            "company": company_data,
            "total_vacancies": total_vacancies
        }

        return data

    except HTTPException as e:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e)

@router.get("/all-vacancies-company-available/{sailor_id}", summary="Все активные вакансии компании для моряка от комании")
async def get_all_vacancies_company(sailor_id: PydanticObjectId, current_user: Optional[dict] = Depends(get_current_user)):
    try:
        if current_user is None or current_user['role'] != "Компания":
            return {
                "vacancies": []
            }

        company_id = current_user.get("id")
        company = await auth.get(company_id)
        company_info = await company_model.get(company.resumeID)

        filter_query = {}
        filter_query["_id"] = {"$in": company_info.vacancies}
        filter_query["is_publish"] = {"$eq": True}
        filter_query["is_active"] = {"$eq": True}

        vacancies = await VacancyModel.find(filter_query).to_list()
        #vacancies_filter = await user_model.get(sailor_id)
        vacancies_out = []
        for vac in vacancies:
            if vac.job_offers is None:
                vac.job_offers = []
            if sailor_id not in vac.job_offers:
                vacancies_out.append(vac)

        #vacancies_filter = await user_model.get(sailor_id)
        #vacancies_out = []
        #for vac in vacancies


        return {
            "vacancies": vacancies_out
        }

    except HTTPException as e:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e)

@router.post("/vacancy-offer/{vacancy_id}/add/{sailor_id}", summary="Пригласить моряка")
async def vacancy_company_add_offer(vacancy_id: PydanticObjectId, sailor_id: PydanticObjectId, current_user: Optional[dict] = Depends(get_current_user)):
    try:
        if current_user is None or current_user['role'] != "Компания":
            return {
                "vacancies": []
            }

        vacancy = await VacancyModel.get(vacancy_id)
        sailor = await user_model.get(sailor_id)

        if vacancy.job_offers is None:
            vacancy.job_offers = []

        if sailor_id not in vacancy.job_offers:
            vacancy.job_offers.append(sailor_id)

        if sailor.offers is None:
            sailor.offers = []
        if vacancy_id not in sailor.offers:
            sailor.offers.append(vacancy_id)

        await vacancy.save()
        await sailor.save()

        return {
            "sailor_id": sailor_id,
            "vacancy_id": vacancy_id
        }

    except HTTPException as e:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e)

@router.post("/vacancy-offer/{vacancy_id}/remove/{sailor_id}", summary="Все активные вакансии компании не паблик")
async def vacancy_company_remove_offer(vacancy_id: PydanticObjectId, sailor_id: PydanticObjectId, current_user: Optional[dict] = Depends(get_current_user)):
    try:
        if current_user is None or current_user['role'] != "Компания":
            return {
                "vacancies": []
            }

        vacancy = await VacancyModel.get(vacancy_id)
        sailor = await user_model.get(sailor_id)

        if vacancy.job_offers is None:
            vacancy.job_offers = []

        if sailor_id in vacancy.job_offers:
            vacancy.job_offers.remove(sailor_id)

        if sailor.offers is None:
            sailor.offers = []
        if vacancy_id in sailor.offers:
            sailor.offers.remove(vacancy_id)

        await vacancy.save()
        await sailor.save()

        return { 1 }

    except HTTPException as e:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e)

@router.get("/company-vacancy-incoming-responses", summary="Входящие отклики на вакансии компании")
async def get_company_vacancy_incoming_responses(current_user: Optional[dict] = Depends(get_current_user)):
    try:

        if current_user is None or current_user['role'] != "Компания":
            return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Авторизуйтесь")

        company_id = current_user.get("id")
        company = await auth.get(company_id)
        company_info = await company_model.get(company.resumeID)

        filter_query = {}
        filter_query["_id"] = {"$in": company_info.vacancies}
        vacancies = await VacancyModel.find(filter_query).to_list()

        incoming_responses = []
        existing_sailors = []
        test = []
        test_users = []

        #outgoing_vacancies = []
        #outgoing_offers = []
        for vac in vacancies:
            if vac.responses:
                filter_query["_id"] = {"$in": vac.responses, "$nin": vac.approved_responses}
                if not vac.approved_responses:
                    vac.approved_responses = []
                #filter_query["_id"] = {"$nin": vac.approved_responses}
                tmp = await user_model.find(filter_query).to_list()
                if tmp:
                    test.append(vac)
                    test_users.append(tmp)


        for vac in vacancies:
            for resp in vac.responses:
                if resp not in vac.approved_responses:
                    if existing_sailors == []:
                        sailor = await user_model.get(resp)
                    else:
                        sailor = False
                        for s in existing_sailors:
                            if s['id'] == resp:
                                sailor = s['sailor']
                        if not sailor:
                            sailor = await user_model.get(resp)
                    existing_sailors.append({
                        "id": resp,
                        "sailor": sailor
                    })
                    incoming_responses.append({
                        "vacancy": vac,
                        "sailor": sailor
                    })

        return {
            "incoming_responses": incoming_responses,
            "vacancies": test,
            "sailors": test_users
        }

    except HTTPException as e:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e)

@router.post("/company-vacancy-incoming-response/{vacancy_id}/accept/{sailor_id}", summary="Принять входящий отклик на вакансию компании")
async def accept_company_vacancy_incoming_responses(vacancy_id: PydanticObjectId, sailor_id: PydanticObjectId, current_user: Optional[dict] = Depends(get_current_user)):
    try:

        if current_user is None or current_user['role'] != "Компания":
            return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Авторизуйтесь")

        vacancy = await VacancyModel.get(vacancy_id)

        if vacancy.approved_responses is None:
            vacancy.approved_responses = []

        if sailor_id not in vacancy.approved_responses:
            vacancy.approved_responses.append(sailor_id)

        await vacancy.save()

        return { 1 }

    except HTTPException as e:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e)

@router.post("/company-vacancy-incoming-response/{vacancy_id}/cancel/{sailor_id}", summary="Принять входящий отклик на вакансию компании")
async def cancel_company_vacancy_incoming_responses(vacancy_id: PydanticObjectId, sailor_id: PydanticObjectId, current_user: Optional[dict] = Depends(get_current_user)):
    try:

        if current_user is None or current_user['role'] != "Компания":
            return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Авторизуйтесь")

        vacancy = await VacancyModel.get(vacancy_id)

        if vacancy.responses is None:
            vacancy.responses = []
        if sailor_id in vacancy.responses:
            vacancy.responses.remove(sailor_id)

        await vacancy.save()

        return { 1 }

    except HTTPException as e:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e)

@router.get("/all-vacancies/vessel/{vessel_id}", summary="Все активные вакансии судна")
async def get_all_vacancies_company(vessel_id: str, page: int = 1, page_size: int = 7):
    try:
        vessel = await NavyModel.find_one({"_id": ObjectId(vessel_id)})

        filter_query = {}
        filter_query["is_publish"] = {"$eq": True}
        filter_query["is_active"] = {"$eq": True}
        filter_query["vessel"] = {"$eq": str(vessel.id)}

        skip = (page - 1) * page_size
        limit = page_size

        total_vacancies = await VacancyModel.find(filter_query).count()
        total_page = math.ceil(total_vacancies / page_size)
        vacancies = await VacancyModel.find(filter_query).skip(skip).limit(limit).to_list()

        vacancies_company = []
        companies_data = []
        for vacancy in vacancies:
            company = await company_model.find_one({'vacancies': vacancy.id})
            if company:
                companies_data.append(CompanySchemas(**company.dict()))
                vacancies_company.append(VacancySchemas(**vacancy.dict()))

        data = {
            "current_page": page,
            "total_pages": total_page,
            "vacancies": vacancies_company,
            "vessel": vessel,
            "companies": companies_data,
            "total_vacancies": total_vacancies
        }

        return data

    except HTTPException as e:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e)


@router.get("/all-vacancies/{vacancies_id}", status_code=status.HTTP_200_OK, summary="Подробнее о вакансии")
async def get_vacancies_id(vacancies_id: PydanticObjectId, current_user: Optional[dict] = Depends(get_current_user)):
    try:

        sailor_approved = False

        data = []

        vacancies = await VacancyModel.find_one({"_id": vacancies_id})

        if not vacancies:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Данная вакансия не найдена")

        data.append(vacancies)
        company = await company_model.find_one({'vacancies': vacancies_id})

        if not company:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Вакансия по данной компании не доступна")

        vessel = await NavyModel.find_one({"_id": ObjectId(vacancies.vessel)})

        filter_query = {}
        filter_query["is_active"] = {"$eq": True}
        filter_query["is_publish"] = {"$eq": True}
        vacancies_count = await VacancyModel.find(filter_query).count()

        #if current_user is not None and current_user['role'] == 'Моряк':
        #    user_id = current_user.get("id")
        #    user_info = await auth.get(user_id)
        #    if user_info.resumeID in

        return {
            "vacancy": vacancies,
            "company_data": company,
            "vessel": vessel,
            "vacancies_count": vacancies_count
        }

    except HTTPException as e:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e)


@router.post('/all-vacancies/{vacancies_id}/respond', summary="Отправить отклик на вакансию")
async def respond_vacancy(vacancies_id: PydanticObjectId, current_user: Optional[dict] = Depends(get_current_user)):
    try:

        if current_user is None or current_user['role'] != 'Моряк':
            return HTTPException(detail="Авторизуйтесь", status_code=status.HTTP_200_OK)

        user_id = current_user.get("id")

        user_info = await auth.get(user_id)

        if not user_info:
            raise HTTPException(detail="User not found", status_code=status.HTTP_401_UNAUTHORIZED)

        resume = await user_model.get(user_info.resumeID)

        if vacancies_id not in resume.responses:
            resume.responses.append(vacancies_id)

        await resume.save()

        vacancy_info = await VacancyModel.get(vacancies_id)

        if not vacancy_info:
            raise HTTPException(detail="Vacancy not found", status_code=status.HTTP_404_NOT_FOUND)

        if vacancy_info.responses:
            vacancy_info.responses.append(user_info.resumeID)
        else:
            vacancy_info.responses = [user_info.resumeID]

        await vacancy_info.save()

        return JSONResponse(content="Отклик на вакансию отправлен", status_code=status.HTTP_200_OK)

    except HTTPException as e:

        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e)

@router.post('/all-vacancies/{vacancies_id}/respond_cancel', summary="Отменить отклик на вакансию")
async def respond_cancel_vacancy(vacancies_id: PydanticObjectId, current_user: Optional[dict] = Depends(get_current_user)):
    try:

        if current_user is None or current_user['role'] != 'Моряк':
            return HTTPException(detail="Авторизуйтесь", status_code=status.HTTP_200_OK)

        user_id = current_user.get("id")

        user_info = await auth.get(user_id)

        if not user_info:
            raise HTTPException(detail="User not found", status_code=status.HTTP_401_UNAUTHORIZED)

        resume = await user_model.get(user_info.resumeID)

        if vacancies_id in resume.responses:
            resume.responses.remove(vacancies_id)

        await resume.save()

        vacancy_info = await VacancyModel.get(vacancies_id)

        if not vacancy_info:
            raise HTTPException(detail="Vacancy not found", status_code=status.HTTP_404_NOT_FOUND)

        if vacancy_info.responses:
            vacancy_info.responses.remove(user_info.resumeID)

        await vacancy_info.save()

        return JSONResponse(content="Отклик на вакансию отменён", status_code=status.HTTP_200_OK)

    except HTTPException as e:

        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e)

@router.get('/all-vacancies-responses', summary="Отклики пользователя")
async def all_vacancy_responses(current_user: Optional[dict] = Depends(get_current_user)):
    try:

        if current_user is None or current_user['role'] != 'Моряк':
            return HTTPException(detail="Авторизуйтесь", status_code=status.HTTP_200_OK)

        user_id = current_user.get("id")

        user_info = await auth.get(user_id)

        if not user_info:
            raise HTTPException(detail="User not found", status_code=status.HTTP_401_UNAUTHORIZED)

        resume = await user_model.get(user_info.resumeID)

        filter_query = {}
        filter_query["_id"] = {"$in": resume.responses}
        vacancies = await VacancyModel.find(filter_query).to_list()

        vessels_data = []
        companies_data = []

        for vacancy in vacancies:
            company = await company_model.find_one({'vacancies': vacancy.id})
            vessel = await NavyModel.find_one({"_id": ObjectId(vacancy.vessel)})
            companies_data.append(CompanySchemas(**company.dict()))
            vessels_data.append(VesselSchemas(**vessel.dict()))

        return {
            "vacancies": vacancies,
            "vessels": vessels_data,
            "companies": companies_data,
        }

    except HTTPException as e:

        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e)



@router.post("/all-vacancies-favorite/company/{company_id}", summary="Добавить компанию в Избранные")
async def add_company_to_favorite(company_id: PydanticObjectId, current_user: Optional[dict] = Depends(get_current_user)):
    try:

        if current_user is None or current_user['role'] == 'Компания':
            return HTTPException(detail="Авторизуйтесь", status_code=status.HTTP_200_OK)

        user_id = current_user.get('id')

        if not user_id:
            raise HTTPException(detail='User not found', status_code=status.HTTP_404_NOT_FOUND)

        user = await auth.get(user_id)

        resume = await user_model.get(user.resumeID)

        if company_id not in resume.favorite_companies:
            resume.favorite_companies.append(company_id)

        await resume.save()

        return {"success": 1}

    except HTTPException as e:

        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e)



@router.post("/all-vacancies-favorite/vacancy/{vacancy_id}", summary="Добавить вакансию в Избранные")
async def add_vacancy_to_favorite(vacancy_id: PydanticObjectId, current_user: Optional[dict] = Depends(get_current_user)):
    try:

        if current_user is None or current_user['role'] == 'Компания':
            return HTTPException(detail="Авторизуйтесь", status_code=status.HTTP_200_OK)

        user_id = current_user.get('id')

        if not user_id:
            raise HTTPException(detail='User not found', status_code=status.HTTP_404_NOT_FOUND)

        user = await auth.get(user_id)

        resume = await user_model.get(user.resumeID)

        if vacancy_id not in resume.favorite_vacancies:
            resume.favorite_vacancies.append(vacancy_id)

        await resume.save()

        return {"success": 1}

    except HTTPException as e:

        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e)


@router.post("/all-vacancies-favorite/company-cancel/{company_id}", summary="Добавить компанию в Избранные")
async def cancel_company_to_favorite(company_id: PydanticObjectId, current_user: Optional[dict] = Depends(get_current_user)):
    try:

        if current_user is None or current_user['role'] == 'Компания':
            return HTTPException(detail="Авторизуйтесь", status_code=status.HTTP_200_OK)

        user_id = current_user.get('id')

        if not user_id:
            raise HTTPException(detail='User not found', status_code=status.HTTP_404_NOT_FOUND)

        user = await auth.get(user_id)

        resume = await user_model.get(user.resumeID)

        if company_id in resume.favorite_companies:
            resume.favorite_companies.remove(company_id)

        await resume.save()

        return {"success": 1}

    except HTTPException as e:

        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e)



@router.post("/all-vacancies-favorite/vacancy-cancel/{vacancy_id}", summary="Убрать вакансию из Избранного")
async def cancel_vacancy_to_favorite(vacancy_id: PydanticObjectId, current_user: Optional[dict] = Depends(get_current_user)):
    try:

        if current_user is None or current_user['role'] != 'Моряк':
            return HTTPException(detail="Авторизуйтесь", status_code=status.HTTP_200_OK)

        user_id = current_user.get('id')

        if not user_id:
            raise HTTPException(detail='User not found', status_code=status.HTTP_404_NOT_FOUND)

        user = await auth.get(user_id)

        resume = await user_model.get(user.resumeID)

        if vacancy_id in resume.favorite_vacancies:
            resume.favorite_vacancies.remove(vacancy_id)

        await resume.save()

        return {"success": 1}

    except HTTPException as e:

        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e)

@router.get("/all-sailor-favorites", summary="Избранное моряк")
async def all_sailor_favorites(current_user: Optional[dict] = Depends(get_current_user)):
    try:

        if current_user is None or current_user['role'] != 'Моряк':
            return HTTPException(detail="Авторизуйтесь", status_code=status.HTTP_200_OK)

        user_id = current_user.get('id')

        if not user_id:
            raise HTTPException(detail='User not found', status_code=status.HTTP_404_NOT_FOUND)

        user = await auth.get(user_id)

        resume = await user_model.get(user.resumeID)

        vacancies_companies = []
        vessels_companies = []
        companies_data = []
        for fav_vacancy in resume.favorite_vacancies:
            vacancy = await VacancyModel.get(fav_vacancy)
            company = await company_model.find_one({'vacancies': vacancy.id})
            vessel = await NavyModel.find_one({"_id": ObjectId(vacancy.vessel)})
            companies_data.append(CompanySchemas(**company.dict()))
            vessels_companies.append(VesselSchemas(**vessel.dict()))
            vacancies_companies.append(VacancySchemas(**vacancy.dict()))

        fav_companies = []
        fav_companies_vacs = []
        filter_query = {}
        filter_query["is_publish"] = {"$eq": True}
        filter_query["is_active"] = {"$eq": True}
        for fav_company in resume.favorite_companies:
            company = await company_model.get(fav_company)
            filter_query["_id"] = {"$in": company.vacancies}
            total_vacancies = await VacancyModel.find(filter_query).count()
            fav_companies.append(company)
            fav_companies_vacs.append(total_vacancies)


        return {
            "vacancies": vacancies_companies,
            "vessels": vessels_companies,
            "companies": companies_data,
            "fav_companies": fav_companies,
            "fav_companies_vacs": fav_companies_vacs
        }

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
            job = await VacancyModel.get(vacancy)

            data.append(job)

        return data

    except HTTPException as e:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e)

@router.get("/company-vacancy-outgoing-offers", summary="Исходящие предложения на вакансии компании")
async def get_company_vacancy_outgoing_offers(current_user: Optional[dict] = Depends(get_current_user)):
    try:

        if current_user is None or current_user['role'] != "Компания":
            return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Авторизуйтесь")

        company_id = current_user.get("id")
        company = await auth.get(company_id)
        company_info = await company_model.get(company.resumeID)

        filter_query = {}
        filter_query["_id"] = {"$in": company_info.vacancies}
        vacancies = await VacancyModel.find(filter_query).to_list()

        outgoing_vacancies = []
        outgoing_offers = []
        for vac in vacancies:
            if vac.job_offers:
                filter_query["_id"] = {"$in": vac.job_offers}
                outgoing_vacancies.append(vac)
                outgoing_offers.append(await user_model.find(filter_query).to_list())

        return {
            "outgoing_vacancies": outgoing_vacancies,
            "outgoing_offers": outgoing_offers
        }

    except HTTPException as e:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e)


@router.post('/all-vacancies/{vacancies_id}/offer_cancel/{sailor_id}', summary="Отменить предложение на вакансию")
async def offer_cancel_vacancy(vacancies_id: PydanticObjectId, sailor_id: PydanticObjectId, current_user: Optional[dict] = Depends(get_current_user)):
    try:

        if current_user is None or current_user['role'] != "Компания":
            return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Авторизуйтесь")

        company_id = current_user.get("id")
        company = await auth.get(company_id)
        company_info = await company_model.get(company.resumeID)

        vacancy = await VacancyModel.get(vacancies_id)
        if not vacancy.job_offers:
            vacancy.job_offers = []

        vacancy.job_offers.remove(sailor_id)
        await vacancy.save()

        return { 1 }

    except HTTPException as e:

        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e)