from fastapi import APIRouter, HTTPException, Query
import math
from starlette import status
from beanie import PydanticObjectId
from bson import ObjectId

from models.vacancy import vacancy as VacancyModel
from models.navy import navy as NavyModel
from models.register import company_model

from schemas.navy.navy import NavyCreate
from schemas.vacancies_company.all_vacancy import VesselSchemas

router = APIRouter()

@router.get("/navy/if-exist-check", summary="Проверка существует ли такое судно в базе", status_code=status.HTTP_200_OK)
async def if_exist_check(vessel_data: NavyCreate):
    try:

        if await NavyModel.find_one({"imo": vessel_data.imo}):
            raise HTTPException(status_code=status.HTTP_200_OK, detail="Судно с таким IMO уже зарегистрировано.")
        if await NavyModel.find_one({"vessel_name": vessel_data.vessel_name}):
            raise HTTPException(status_code=status.HTTP_200_OK, detail="Судно с таким наименованием уже зарегистрировано.")

        return True

    except HTTPException as e:
        raise HTTPException(detail=str(e), status_code=status.HTTP_400_BAD_REQUEST)

@router.post("/navy/register", summary="Добавление судна", status_code=status.HTTP_200_OK)
async def register_vessel(vessel_data: NavyCreate):
    try:

        if await NavyModel.find_one({"imo": vessel_data.imo}):

            raise HTTPException(status_code=status.HTTP_200_OK, detail="Судно с таким IMO уже зарегистрировано.")

        vessel = NavyModel(**vessel_data.dict())

        await vessel.create()

        if vessel_data.append_company:

            company = await company_model.find_one({"email": vessel_data.company_email})
            vessel_list = company.vessel

            if vessel.id not in vessel_list:
                vessel_list.append(vessel.id)

            await company.update({"$set": {"vessel": vessel_list}})

        return vessel

    except HTTPException as e:
        raise HTTPException(detail=str(e), status_code=status.HTTP_400_BAD_REQUEST)


@router.post("/navy/register_existing", summary="Добавление существующего судна", status_code=status.HTTP_200_OK)
async def register_existing_vessel(id: PydanticObjectId, email: str):
    try:

        company = await company_model.find_one({"email": email})
        vessel_list = company.vessel
        if id not in vessel_list:
            vessel_list.append(id)

        await company.update({"$set": {"vessel": vessel_list}})

        return company

    except HTTPException as e:
        raise HTTPException(detail=str(e), status_code=status.HTTP_400_BAD_REQUEST)


@router.put("/navy/remove_existing", summary="Удаление существующего судна", status_code=status.HTTP_200_OK)
async def remove_existing_vessel(id: PydanticObjectId, email: str):
    try:

        company = await company_model.find_one({"email": email})
        vessel_list = company.vessel

        vessel_list.remove(id)

        await company.update({"$set": {"vessel": vessel_list}})

        return company

    except HTTPException as e:
        raise HTTPException(detail=str(e), status_code=status.HTTP_400_BAD_REQUEST)


@router.put("/navy/remove_moderate", summary="Удаление существующего судна", status_code=status.HTTP_200_OK)
async def remove_moderate_vessel(id: PydanticObjectId, email: str):
    try:

        company = await company_model.find_one({"email": email})
        vessel_list = company.vessel

        vessel_list.remove(id)

        await company.update({"$set": {"vessel": vessel_list}})

        vessel = await NavyModel.get(id)
        await vessel.delete()

        return company

    except HTTPException as e:
        raise HTTPException(detail=str(e), status_code=status.HTTP_400_BAD_REQUEST)

@router.get("/navy/unregistered", summary="Список судов флота не привязанных к компании", status_code=status.HTTP_200_OK)
async def unregistered_vessel(email: str):
    try:

        vessels = await NavyModel.find().to_list()
        company = await company_model.find_one({"email": email})
        vessel_list = company.vessel

        vessels_out = []
        for vessel in vessels:
            if vessel.id not in vessel_list:
                vessels_out.append(vessel)

        return vessels_out

    except HTTPException as e:
        raise HTTPException(detail=str(e), status_code=status.HTTP_400_BAD_REQUEST)


@router.get("/navy/registered", summary="Список судов флота привязанных к компании", status_code=status.HTTP_200_OK)
async def registered_vessel(email: str):
    try:

        vessels = await NavyModel.find().to_list()
        company = await company_model.find_one({"email": email})

        vessel_list = company.vessel

        vessels_out = []
        for vessel in vessels:
            if vessel.id in vessel_list:
                vessels_out.append(vessel)

        return vessels_out

    except HTTPException as e:
        raise HTTPException(detail=str(e), status_code=status.HTTP_400_BAD_REQUEST)


@router.get("/all-navy", summary="Список судов флота", status_code=status.HTTP_200_OK)
async def get_all_navy(page: int = 1, page_size: int = 7, search: str = Query(None), is_publish: bool = Query(True), is_active: bool = Query(True)):
    try:
        filter_query = {}
        if search:
            filter_query["vessel_name"] = {"$regex": search, "$options": "i"}
        filter_query["is_active"] = {"$eq": True}
        skip = (page - 1) * page_size
        limit = page_size

        total_vessels = await NavyModel.find(filter_query).count()
        total_page = math.ceil(total_vessels / page_size)
        vessels = await NavyModel.find(filter_query).skip(skip).limit(limit).to_list()

        filter_query_vac = {}
        filter_query_vac["is_publish"] = {"$eq": True}
        filter_query_vac["is_active"] = {"$eq": True}

        vessels_data = []
        vacancies_data = []
        for vessel in vessels:
            filter_query_vac["vessel"] = {"$eq": str(vessel.id)}
            vacancies = await VacancyModel.find(filter_query_vac).count()
            vessels_data.append(VesselSchemas(**vessel.dict()))
            vacancies_data.append(vacancies)

        return {
            "vessels_data": vessels_data,
            "vacancies_data": vacancies_data,
            "current_page": page,
            "total_pages": total_page,
        }

    except HTTPException as e:
        raise HTTPException(detail=str(e), status_code=status.HTTP_400_BAD_REQUEST)