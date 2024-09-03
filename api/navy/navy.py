from fastapi import APIRouter, HTTPException
from starlette import status
from api.navy.schemas import ResponseNavy, NavyInfo, CompanyInfo
from models import company_model

router = APIRouter()


@router.get('/navy', summary="Морской флот", status_code=status.HTTP_200_OK)
async def get_navy(page: int = 1, page_size: int = 10):
    try:
        company_navy = []
        company_info = await company_model.find().to_list()

        for company in company_info:
            for vessel in company.vessel:
                navy_info = NavyInfo(
                    id=vessel.id,
                    ship_name=vessel.ship_name,
                    ship_type=vessel.ship_type,
                    year_built=vessel.year_built,
                    dwt=vessel.dwt,
                    imo=vessel.imo
                )
                company_info = CompanyInfo(
                    id=company.id,
                    company_name=company.company_name,
                    photo_path=company.photo_path
                )
                open_vacancy = len([vacancy for vacancy in company.vacancies])
                response_navy = ResponseNavy(
                    companyInfo=company_info,
                    navyInfo=navy_info,
                    openVacancy=open_vacancy
                )
                company_navy.append(response_navy.dict())

        return company_navy[(page - 1) * page_size:page * page_size]

    except Exception as e:
        return HTTPException(detail=str(e), status_code=status.HTTP_400_BAD_REQUEST)