from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from api.auth.config import get_current_user
from typing import Annotated, List, Optional
from models import auth, user_model, company_model
from schemas.balance.payment_details import PaymentDetails, PaymentHistory
from api.balance_and_history_payment.schemas import PaymentCreateSchemas
from api.yookassa.request import create_payment

router = APIRouter()


@router.get('/balance', status_code=status.HTTP_200_OK,
            summary="Возвращает баланс пользователя и компании")
async def balance_sailor_company(current_user: Optional[dict] = Depends(get_current_user)):
    try:

        if current_user is None:
            return HTTPException(detail="Unauthorized", status_code=status.HTTP_401_UNAUTHORIZED)

        if current_user['role'] == "Моряк":
            user_id = current_user.get('id')

            user_info = await auth.get(user_id)

            if not user_info:

                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

            resume = await user_model.get(user_info.resumeID)

            count_history = sum(resume.payment_history) if resume.payment_history else 0


            data = PaymentDetails(
                balance=resume.balance,
                autofill=resume.autofill,
                count_history=count_history,
            )

            return data

        else:
            company_id = current_user.get('id')

            company_info = await auth.get(company_id)

            if not company_info:

                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

            resume = await company_model.get(company_info.resumeID)

            count_history = sum(resume.payment_history) if resume.payment_history else 0


            data = PaymentDetails(
                balance=resume.balance,
                autofill=resume.autofill,
                count_history=count_history,
            )

            return data

    except HTTPException as e:
        return HTTPException(detail=e, status_code=status.HTTP_400_BAD_REQUEST)


@router.post("/balance/payment", summary="Пополнение баланса", status_code=status.HTTP_201_CREATED)
async def create_payment_endpoint(request: PaymentCreateSchemas, current_user: dict = Depends(get_current_user)):

    try:

        if current_user is None:
            return HTTPException(detail="Unauthorized", status_code=status.HTTP_401_UNAUTHORIZED)

        if current_user['role'] == "Моряк":

            user_id = current_user.get('id')

            user_info = await auth.get(user_id)

            if not user_info:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

            reference = await create_payment(value=request.amount, description=request.description)

            return {"reference": reference}

        elif current_user['role'] == "Компания":
            company_id = current_user.get('id')

            user_info = await auth.get(company_id)

            if not user_info:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

            reference = await create_payment(value=request.amount, description=request.description)

            return {"reference": reference}

        else:
            pass
    except HTTPException as e:
        return HTTPException(detail=e, status_code=status.HTTP_400_BAD_REQUEST)


@router.get('/balance/history', response_model=List[PaymentHistory], status_code=status.HTTP_200_OK,
            summary="Возваращает историю пополнение пользователя и компании")
async def history_payment(current_user: Annotated[dict, Depends(get_current_user)]):
    try:

        if current_user is None:
            return HTTPException(detail="Unauthorized", status_code=status.HTTP_401_UNAUTHORIZED)

        if current_user['role'] == "Моряк":

            user_id = current_user.get('id')

            user_info = await auth.get(user_id)

            if not user_info:

                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

            resume = await user_model.get(user_info.resumeID)

            history = resume.payment_history if resume.payment_history is not None else []

            return history

        else:
            company_id = current_user.get('id')

            company_info = await auth.get(company_id)

            if not company_info:

                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

            resume = await company_model.get(company_info.resumeID)

            history = resume.payment_history if resume.payment_history is not None else []

            return history

    except HTTPException as e:
        return HTTPException(detail=e, status_code=status.HTTP_400_BAD_REQUEST)
