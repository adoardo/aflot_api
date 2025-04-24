from fastapi import APIRouter, Depends, HTTPException
from api.auth.config import get_current_user
from typing import Optional
from starlette import status
from .schemas import OffersSailor, OffersCompanyInfo, ResponsesOffers, Response, OfferID
from models import user_model, auth, company_model
from models.vacancy import vacancy as VacancyModel
from beanie import PydanticObjectId

router = APIRouter()


@router.get('/offers', status_code=status.HTTP_200_OK, summary="Возвращает входящие предложения для моряка")
async def get_offers(current_user: Optional[dict] = Depends(get_current_user)):
    try:

        if current_user is None or current_user['role'] == "Компания":

            return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Нет доступа")

        user_id = current_user.get('id')

        user_info = await auth.get(user_id)

        if not user_info:

            return HTTPException(detail="User not found", status_code=status.HTTP_401_UNAUTHORIZED)

        resume_id = user_info.resumeID

        resume_info = await user_model.get(resume_id)

        offers = resume_info.offers
        count_offers = len(offers)

        if offers is None:
            return []

        offers = []

        for offer_id in resume_info.offers:
            company = await company_model.find_one({"vacancies": offer_id})
            vacancy = await VacancyModel.get(offer_id)

            data = ResponsesOffers(
                offers=OffersSailor(**vacancy.dict()),
                companyInfo=OffersCompanyInfo(**company.dict())
            )

            offers.append(data)

        return Response(offers=offers, countIncoming=f"ожидают {count_offers} вакансии")

    except HTTPException as e:
        return HTTPException(detail=str(e), status_code=status.HTTP_400_BAD_REQUEST)


@router.get('/offers/{offer_id}', status_code=status.HTTP_200_OK, summary="Возвращает оффер по ID")
async def get_offer_id(offer_id: PydanticObjectId, current_user: Optional[dict] = Depends(get_current_user)):
    try:

        if current_user is None or current_user['role'] == "Компания":

            return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Нет доступа")

        user_id = current_user.get('id')

        user_info = await auth.get(user_id)

        if not user_info:
            return HTTPException(detail="User not found", status_code=status.HTTP_401_UNAUTHORIZED)

        offer = await VacancyModel.get(offer_id)

        return OfferID(**offer.dict())

    except HTTPException as e:
        return HTTPException(detail=str(e), status_code=status.HTTP_400_BAD_REQUEST)
