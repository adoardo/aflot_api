from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, List
from api.auth.config import get_current_user
from starlette import status
from models import swims_tariffs, description_tariffs, company_tariffs, auth, user_model, company_model, paymentHistory
from .schemas import PaymentSchemas
from api.yookassa.request import create_payment as get_url

router = APIRouter()


@router.get("/tariffs/company", status_code=status.HTTP_200_OK, response_model=List[company_tariffs],
            summary="Тарифы компании")
async def get_tariffs_company():
    try:

        tariffs = await company_tariffs.find().to_list()

        if not tariffs:
            raise HTTPException(detail="No tariffs found", status_code=status.HTTP_404_NOT_FOUND)

        return tariffs

    except HTTPException as e:

        return HTTPException(detail=e, status_code=status.HTTP_400_BAD_REQUEST)


@router.get("/tariffs/sailor", status_code=status.HTTP_200_OK, summary="Тарифы моряка")
async def get_tariffs_swims():
    try:

        data = []

        tariffs = await swims_tariffs.find().to_list()

        if not tariffs:
            raise HTTPException(detail="No tariffs found", status_code=status.HTTP_404_NOT_FOUND)

        data.append(tariffs)
        descriptions = await description_tariffs.find().to_list()

        if not descriptions:
            raise HTTPException(detail="No descriptions found", status_code=status.HTTP_404_NOT_FOUND)

        data.append(descriptions)
        return data
    except HTTPException as e:

        return HTTPException(detail=e, status_code=status.HTTP_400_BAD_REQUEST)


@router.post("/tariffs/pay", summary="Оплата тарифа для всех пользователей", status_code=status.HTTP_200_OK)
async def create_payment(request: PaymentSchemas, current_user: dict = Depends(get_current_user)):
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Авторизуйтесь")

    user_id = current_user.get('id')
    user_info = await auth.get(user_id)
    resume_id = user_info.resumeID

    resume = await user_model.get(resume_id) or await company_model.get(resume_id)
    if resume:
        new_receipt = paymentHistory(
            product=request.description,
            resumeID=resume.id,
            amount=request.amount,
        )
        await new_receipt.insert()
        url = await get_url(request.amount, request.description, new_receipt.id)
        return url

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")