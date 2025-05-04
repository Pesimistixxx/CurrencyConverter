import httpx
from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates

from app.api.schemas.exchange import CreateExchange
from app.core.security import get_user_from_cookie

exchanger_router = APIRouter(prefix='/exchanger', tags=['exchanger'])
templates = Jinja2Templates(directory='templates')


async def get_exchanger_data(
        amount_from: float = Form(),
        currency_from: str = Form(),
        currency_to: str = Form()
) -> CreateExchange:
    return CreateExchange(
        from_val=currency_from,
        to_val=currency_to,
        amount=amount_from
    )


# @exchanger_router.post('')
# async def exchange_values(exchange_inp: CreateExchange = Depends(get_exchanger_data),
#                           user: str = Depends(get_user_from_cookie)):
#     url = f'https://api.apilayer.com/currency_data/convert?to={exchange_inp.to_val}&from={exchange_inp.from_val}&amount={exchange_inp.amount}'
#     headers = {
#         "apikey": settings.API_KEY
#     }
#     async with httpx.AsyncClient() as client:
#         response = await client.get(
#             url,
#             headers=headers
#         )
#         return JSONResponse(
#             content=response.json(),
#             headers={"X-Requested-With": "XMLHttpRequest"}
#         )

@exchanger_router.post('')
async def exchange_test(exchange_inp: CreateExchange = Depends(get_exchanger_data),
                        user: str = Depends(get_user_from_cookie)):
    url = 'https://www.cbr-xml-daily.ru/daily_json.js'
    async with httpx.AsyncClient() as client:
        response = await client.get(
            url
        )
    if exchange_inp.to_val == 'RUB':
        well_to = 1
    else:
        well_to = response.json()['Valute'][exchange_inp.to_val]['Value']
    if exchange_inp.from_val == 'RUB':
        well_from = 1
    else:
        well_from = response.json()['Valute'][exchange_inp.from_val]['Value']
    to_val = well_from / well_to * exchange_inp.amount
    json_dict = {'amount_to': to_val}
    return JSONResponse(
        content=json_dict,
        headers={"X-Requested-With": "XMLHttpRequest"}
    )


@exchanger_router.get('')
async def exchange_get(request: Request, user: str = Depends(get_user_from_cookie)):
    return templates.TemplateResponse('converter.html', {'request': request, 'username': user})