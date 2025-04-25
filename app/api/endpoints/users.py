import bcrypt
from fastapi import APIRouter, status, Depends, HTTPException
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select
from passlib.context import CryptContext

from app.api.database.db_depends import get_db
from app.api.schemas.user import CreateUser, AuthUser
from app.api.database.db_models import User_model
from app.core.security import create_jwt_token

user_router = APIRouter(prefix='/auth', tags=['auth'])
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


@user_router.post('/register', status_code=status.HTTP_201_CREATED)
async def create_user(db: Annotated[AsyncSession, Depends(get_db)],
                      create_user: CreateUser):
    await db.execute(insert(User_model).values(
        username=create_user.username,
        email=create_user.email,
        password=bcrypt_context.hash(create_user.password),
    ))
    await db.commit()
    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Successful'
    }


@user_router.post('/login')
async def login_user(db: Annotated[AsyncSession, Depends(get_db)], user_inp: AuthUser):
    user_find = await db.scalar(select(User_model).where(User_model.username == user_inp.username))
    if user_find is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='user not found'
        )
    if not bcrypt.checkpw(user_inp.password.encode('utf-8'), user_find.password.encode('utf-8')):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='invalid credentials'
        )
    token = create_jwt_token(user_find.username)
    return {
        'access_token': token,
        'token_type': 'bearer'
    }

