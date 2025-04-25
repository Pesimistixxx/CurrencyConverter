from fastapi import APIRouter, Depends, status
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, desc
import httpx

from app.core.security import get_user_from_token
from app.api.schemas.post import CreatePost
from app.api.database.db_models import Post_moodel
from app.api.database.db_depends import get_db

profile_router = APIRouter(prefix='/profile', tags=['profile'])


@profile_router.get('/', status_code=status.HTTP_200_OK)
async def get_user_profile(db: Annotated[AsyncSession, Depends(get_db)], user: str = Depends(get_user_from_token)):
    posts = await db.scalars(select(Post_moodel)
                             .where(Post_moodel.username == user, Post_moodel.is_active == True)
                             .order_by(desc('id')).limit(3))
    return {
        'username': user,
        'last posts': posts.all(),
        'message': 'success'
    }


@profile_router.post('/posts', status_code=status.HTTP_201_CREATED)
async def create_user_post(db: Annotated[AsyncSession, Depends(get_db)],
                           post_inp: CreatePost,
                           user: str = Depends(get_user_from_token)):
    await db.execute(insert(Post_moodel).values(
        username=user,
        text=post_inp.text,
    ))
    await db.commit()
    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Successful'
    }


@profile_router.get('/posts')
async def create_user_post(db: Annotated[AsyncSession, Depends(get_db)],
                           user: str = Depends(get_user_from_token)):
    posts = await db.scalars(select(Post_moodel)
                             .where(Post_moodel.username == user, Post_moodel.is_active == True)
                             .order_by(desc('id')))

    return {
        'posts': posts.all()
    }


@profile_router.get('/exchanger')
async def exchange_values(user: str = Depends(get_user_from_token)):
    async with httpx.AsyncClient() as client:
        response = await client.get('https://api.apilayer.com/currency_data/convert')
        return response.json()
