from fastapi import APIRouter, HTTPException, Depends

from api.auth.config import get_current_user
from models import position, vessel, auth, company_model
from starlette import status
from typing import List, Annotated

router = APIRouter()


@router.get("/settings", status_code=status.HTTP_200_OK)
async def get_settings():
    try:

        data_list = []

        position_models = await position.find().to_list()

        if position_models:

            data_list.append(position_models)
        else:

            pass

        vessel_models = await vessel.find().to_list()

        if vessel_models:

            data_list.append(vessel_models)
        else:

            pass

        return data_list
    except HTTPException as e:
        return HTTPException(detail=e, status_code=status.HTTP_400_BAD_REQUEST)


@router.get("/company-ship", status_code=status.HTTP_200_OK, summary="Возвращает список короблей компании")
async def get_company_ship(current_user: Annotated[dict, Depends(get_current_user)]):
    try:


        company_id = current_user.get('id')
        company_info = await auth.get(company_id)

        if not company_info:
            raise HTTPException(detail="Company not found", status_code=status.HTTP_404_NOT_FOUND)

        company = await company_model.get(company_info.resumeID)

        vessels = company.vessel

        if vessels is None:

            return []

        return vessels

    except HTTPException as e:
        return HTTPException(detail=e, status_code=status.HTTP_400_BAD_REQUEST)