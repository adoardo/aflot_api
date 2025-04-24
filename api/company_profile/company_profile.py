from fastapi import Depends, HTTPException, APIRouter
from starlette.responses import JSONResponse
from starlette import status
from .schemas import NewShipSchema, MyNavy, ResponseMyNavy
from beanie import PydanticObjectId
from models import auth, company_model, navy
from schemas.profile.profile_company import CompanyOldSettings
from typing import Optional
from api.auth.config import get_current_user
from schemas.profile.profile_company import CompanySchema

router = APIRouter()


@router.get("/profile", status_code=status.HTTP_200_OK, response_model=CompanySchema,
            summary="Возвращает профиль компании")
async def get_company_profile(current_user: Optional[dict] = Depends(get_current_user)):
    try:

        if current_user is None or current_user['role'] != "Компания":
            return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

        company_id = current_user.get('id')

        company_info = await auth.get(company_id)

        if not company_info:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Company not found")

        resume = await company_model.get(company_info.resumeID)

        return resume

    except HTTPException as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))


@router.get("/profile/settings", status_code=status.HTTP_200_OK, response_model=CompanyOldSettings,
            summary="Возвращает ДОП настройки профиля компании")
async def get_company_old_settings(current_user: Optional[dict] = Depends(get_current_user)):
    try:

        if current_user is None or current_user['role'] != "Компания":
            return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

        company_id = current_user.get('id')

        company_info = await auth.get(company_id)

        if not company_info:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Company not found")

        resume = await company_model.get(company_info.resumeID)

        return resume

    except HTTPException as e:

        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e)


@router.put("/profile/settings/save", status_code=status.HTTP_200_OK, response_model=CompanyOldSettings,
            summary="Изменение ДОП настроек профиля компании")
async def save_company_profile(request: CompanyOldSettings, current_user: Optional[dict] = Depends(get_current_user)):
    try:

        if current_user is None or current_user['role'] != "Компания":
            return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

        company_id = current_user.get('id')

        company_info = await auth.get(company_id)

        if not company_info:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Company not found")

        resume = await company_model.get(company_info.resumeID)

        request = {k: v for k, v in request.dict().items() if v is not None}

        update_query = {"$set": {
            field: value for field, value in request.items()
        }}

        await resume.update(update_query)
        await company_info.update(update_query)

        return company_info
    except HTTPException as e:

        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e)


@router.get("/profile/navy", status_code=status.HTTP_200_OK, summary="Возвращает судна компании")
async def get_my_navy(current_user: Optional[dict] = Depends(get_current_user)):
    try:

        if current_user is None or current_user['role'] != "Компания":
            return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

        company_id = current_user.get('id')

        company_info = await auth.get(company_id)

        if not company_info:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Company not found")

        resume = await company_model.get(company_info.resumeID)

        vessels = resume.vessel

        response_my_navy = []

        for vessel in vessels:
            response_my_navy.append(MyNavy(**vessel.dict()))

        response_navy_moderation = []

        moderations = await moderation_navy.find({"company_id": company_info.resumeID}).to_list()

        for moderation in moderations:
            response_navy_moderation.append(MyNavy(**moderation.dict()))

        return ResponseMyNavy(myNavy=response_my_navy, moderationNavy=response_navy_moderation)
    except HTTPException as e:

        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/profile/navy/{navy_id}", summary="Подребнее о судне", status_code=status.HTTP_200_OK)
async def get_my_navy_by_id(navy_id: PydanticObjectId, current_user: Optional[dict] = Depends(get_current_user)):
    try:

        if current_user is None or current_user['role'] != "Компания":
            return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

        company_id = current_user.get('id')

        company_info = await auth.get(company_id)

        if not company_info:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Company not found")

        resume = await company_model.get(company_info.resumeID)

        vessel = next((v for v in resume.vessel if v.id == navy_id), None)

        if vessel is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vessel not found")

        return vessel

    except HTTPException as e:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/profile/navy/{navy_id}/delete", status_code=status.HTTP_204_NO_CONTENT,
               summary="Удаление судов из раздела Мои суда")
async def delete_my_navy(navy_id: PydanticObjectId, current_user: Optional[dict] = Depends(get_current_user)):
    try:

        if current_user is None or current_user['role'] != "Компания":
            return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

        company_id = current_user.get('id')

        company_info = await auth.get(company_id)

        if not company_info:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Company not found")

        resume = await company_model.get(company_info.resumeID)

        await company_model.update(resume, {"$pull": {"vessel": {"id": navy_id}}})

        return {"message": f"{navy_id} deleted successfully"}

    except HTTPException as e:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/profile/navy/moderation/{navy_id}", summary="Подробнее о судне в разделе модерации",
            status_code=status.HTTP_200_OK, response_model=MyNavy)
async def get_navy_moderation_by_id(navy_id: PydanticObjectId,
                                    current_user: Optional[dict] = Depends(get_current_user)):
    try:

        if current_user is None or current_user['role'] != "Компания":
            return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

        vessel = await moderation_navy.get(navy_id)

        return vessel

    except HTTPException as e:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/profile/navy/moderation/{navy_id}/cancel", summary="Отменить запрос на модерацию",
               status_code=status.HTTP_204_NO_CONTENT)
async def cancel_maderation_navy(navy_id: PydanticObjectId, current_user: dict = Depends(get_current_user)):
    try:
        if current_user is None or current_user['role'] != "Компания":
            return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

        moderation_navy_doc = await moderation_navy.get(navy_id)

        if moderation_navy_doc:
            await moderation_navy_doc.delete()

        return {"message": f"{navy_id} cancelled successfully"}

    except HTTPException as e:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/profile/navy/add-my-ship", status_code=status.HTTP_201_CREATED,
             summary="Добавить судно в ручную")
async def add_my_ship(request: NewShipSchema, current_user: Optional[dict] = Depends(get_current_user)):
    try:

        if current_user is None or current_user['role'] != "Компания":
            return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

        company_id = current_user.get('id')

        company_info = await auth.get(company_id)

        if not company_info:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Company not found")

        moderation_navy_obj = moderation_navy(
            company_id=company_info.resumeID,
            vessel_name=request.vessel_name,
            imo=request.imo,
            ship_type=request.ship_type,
            year_built=request.year_built,
            dwt=request.dwt,
            kw=request.kw,
            length=request.length,
            width=request.width
        )
        await moderation_navy_obj.save()

        return moderation_navy_obj

    except HTTPException as e:
        return HTTPException(detail=str(e), status_code=status.HTTP_400_BAD_REQUEST)


@router.get("/profile/navy/ship", status_code=status.HTTP_200_OK, summary="Возвращает список «Морского флота»")
async def get_navy_list(current_user: Optional[dict] = Depends(get_current_user)):
    try:

        if current_user is None or current_user['role'] != "Компания":
            return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

        navy_list = await navy.find_all().to_list()

        return navy_list

    except HTTPException as e:
        return HTTPException(detail=str(e), status_code=status.HTTP_400_BAD_REQUEST)


@router.post("/profile/navy/ship", status_code=status.HTTP_201_CREATED,
             summary="Добавить судно из «Морского флота»")
async def add_ship_navy(current_user: Optional[dict] = Depends(get_current_user)):
    try:

        pass

    except HTTPException as e:
        return HTTPException(detail=str(e), status_code=status.HTTP_400_BAD_REQUEST)
