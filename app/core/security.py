from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
import jwt
import datetime
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy import select

from app.api.database.db_models import User_model
from app.api.database.db_depends import get_db
from app.api.schemas.user import AuthUser
from app.core.config import settings


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

ALGORITHM = 'HS256'
SECRET_KEY = settings.SECRET_KEY
ACCESS_TOKEN_EXPIRE_MINUTES = 20


def get_user(db: Annotated[AsyncSession, Depends(get_db)], user_inp: AuthUser):
    user_find = db.scalar(select(User_model).where(User_model.username == user_inp.username,
                                                   User_model.password == bcrypt_context.hash(user_inp.password)))
    if not user_find:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User with this login and password not found'
        )
    return user_find


def get_user_from_cookie(request: Request):
    token = request.cookies.get("auth_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="expired token"
        )
    except jwt.exceptions.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


def create_jwt_token(username: str):
    expire = datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(payload={'sub': username, 'exp': expire}, key=SECRET_KEY, algorithm=ALGORITHM)
