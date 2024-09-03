from fastapi import APIRouter, Depends, HTTPException
from models.db import db
from beanie import PydanticObjectId
from starlette import status
from typing import Annotated, Optional, List
from api.auth.config import get_current_user
from models import user_model, auth, ship, company_model
from schemas.favorites_swims.company import CompanyFavoritesSchemas

router = APIRouter()


@router.get('/favorite/vacancies', summary="Возвращает избранные вакансии")
async def get_favorite_vacancies(current_user: Annotated[dict, Depends(get_current_user)]):
    try:

        user_id = current_user.get("id")

        user = await auth.get(user_id)

        if not user:

            raise HTTPException(detail="User not found", status_code=status.HTTP_401_UNAUTHORIZED)

        resume = await user_model.get(user.resumeID)

        favorite_vacancy = resume.favorites_vacancies

        vacancy_list = []
        for vac in favorite_vacancy:
            vacancy = await ship.get(vac.id)
            vacancy_list.append(vacancy)

        return vacancy_list
    except HTTPException as e:
        return HTTPException(detail=e, status_code=status.HTTP_400_BAD_REQUEST)


@router.get('/favorite/company', response_model=List[CompanyFavoritesSchemas], status_code=status.HTTP_200_OK,
            summary="Возвращает избранные компании")
async def get_favorite_company(current_user: Annotated[dict, Depends(get_current_user)]):
    try:

        user_id = current_user.get("id")

        user = await auth.get(user_id)

        if not user:

            raise HTTPException(detail="User not found", status_code=status.HTTP_401_UNAUTHORIZED)

        resume = await user_model.get(user.resumeID)

        favorite_company = resume.favorites_company

        company_list = []
        for com in favorite_company:
            count = 0

            company = await company_model.get(com.id)

            for vac in company.vacancies:
                vacancy = await ship.get(vac.id)

                if vacancy.status == 'активная вакансия':
                    count += 1

            date_joinde = user.date_joined.strftime("%d.%m.%Y")
            schemas = CompanyFavoritesSchemas(
                id=company.id,
                company_name=company.company_name,
                company_address=company.company_address,
                date_joined=date_joinde,
                active_vacancy=count
            )
            company_list.append(schemas)

        return company_list

    except HTTPException as e:
        return HTTPException(detail=e, status_code=status.HTTP_400_BAD_REQUEST)


@router.delete('/favorite/company/{company_id}/delete', status_code=status.HTTP_200_OK,
               summary="Удаляет компанию из избранных")
async def delete_favorite_company(company_id: PydanticObjectId, current_user: Annotated[dict, Depends(get_current_user)]):
    try:

        user_id = current_user.get("id")
        user_info = await auth.get(user_id)

        if not user_info:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Данная компания не зарегистрирована")

        resume = await user_model.get(user_info.resumeID)

        await user_model.update(resume, {"$pull": {"favorites_company": {"id": company_id}}})

        return {"message": f"{company_id} - deleted successfully from favorites"}

    except HTTPException as e:
        return HTTPException(detail=e, status_code=status.HTTP_400_BAD_REQUEST)
