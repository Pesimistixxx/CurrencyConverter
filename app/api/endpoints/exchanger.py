import httpx
from fastapi import APIRouter, Depends

from app.api.schemas.exchange import CreateExchange
from app.core.config import settings
from app.core.security import get_user_from_token

exchanger_router = APIRouter(prefix='/exchanger', tags=['exchanger'])


@exchanger_router.post('/exchanger')
async def exchange_values(exchange_inp: CreateExchange, user: str = Depends(get_user_from_token)):
    url = f'https://api.apilayer.com/currency_data/convert?to={exchange_inp.to_val}&from={exchange_inp.from_val}&amount={exchange_inp.amount}'
    headers = {
        "apikey": settings.API_KEY
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(
            url,
            headers=headers
        )
        return response.json()
