import bcrypt
from fastapi import APIRouter, status, Depends, HTTPException, Request, Form
from fastapi.templating import Jinja2Templates
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select
from passlib.context import CryptContext
from starlette.responses import HTMLResponse, RedirectResponse

from app.api.database.db_depends import get_db
from app.api.schemas.user import CreateUser, AuthUser
from app.api.database.db_models import User_model
from app.core.security import create_jwt_token

user_router = APIRouter(prefix='/auth', tags=['auth'])
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
templates = Jinja2Templates(directory='templates')


async def get_user_data_register(
        username: str = Form(),
        email: str = Form(),
        password: str = Form()
) -> CreateUser:
    return CreateUser(
        username=username,
        email=email,
        password=password
    )


async def get_user_data_login(
        username: str = Form(),
        password: str = Form()
) -> AuthUser:
    return AuthUser(
        username=username,
        password=password
    )


@user_router.get('/register', response_class=HTMLResponse)
async def get_registration(request: Request):
    return templates.TemplateResponse("register.html", {'request': request})


@user_router.post('/register', status_code=status.HTTP_201_CREATED)
async def create_user(db: Annotated[AsyncSession, Depends(get_db)],
                      user_inp: CreateUser = Depends(get_user_data_register)):
    await db.execute(insert(User_model).values(
        username=user_inp.username,
        email=user_inp.email,
        password=bcrypt_context.hash(user_inp.password),
    ))
    await db.commit()
    return RedirectResponse('/auth/login', status_code=303)


@user_router.get('/login', response_class=HTMLResponse)
async def get_login(request: Request):
    return templates.TemplateResponse("login.html", {'request': request})


@user_router.post('/login')
async def login_user(db: Annotated[AsyncSession, Depends(get_db)],
                     user_inp: AuthUser = Depends(get_user_data_login)):
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
    response = RedirectResponse('/profile', status_code=303)
    response.set_cookie(
        key="auth_token",
        value=token,
        httponly=True,
        secure=False,
        max_age=3600,
        samesite="none",
        path='/'
    )
    return response
