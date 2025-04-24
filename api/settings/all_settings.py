from fastapi import APIRouter, HTTPException, Depends
from starlette import status
from models.global_settings import settings_global
from beanie import PydanticObjectId


router = APIRouter()


@router.get('/available-jobs', summary="Получить список должностей")
async def get_available_jobs():
    try:

        res = await settings_global.find({"option_slug": "option_jobs"}).to_list()

        return {"data": res}

    except HTTPException as e:
        return HTTPException(detail=e, status_code=status.HTTP_400_BAD_REQUEST)


@router.get('/ship-types', summary="Получить список судов")
async def get_available_ships():
    try:

        res = await settings_global.find({"option_slug": "option_ship_types"}).to_list()

        return {"data": res}

    except HTTPException as e:
        return HTTPException(detail=e, status_code=status.HTTP_400_BAD_REQUEST)


@router.get('/contract-duration', summary="Получить список длительностей контракта")
async def get_contract_duration():
    try:

        res = await settings_global.find({"option_slug": "option_contract_duration"}).to_list()

        return {"data": res}

    except HTTPException as e:
        return HTTPException(detail=e, status_code=status.HTTP_400_BAD_REQUEST)

