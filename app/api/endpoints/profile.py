from fastapi import APIRouter, Depends, status, Request, Response, Path
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.core.security import get_user_from_cookie
from app.api.database.db_models import Post_moodel
from app.api.database.db_depends import get_db

profile_router = APIRouter(prefix='/profile', tags=['profile'])
templates = Jinja2Templates(directory="templates")


@profile_router.get('/', status_code=status.HTTP_200_OK, response_class=HTMLResponse)
async def get_user_profile(request: Request,
                           db: Annotated[AsyncSession, Depends(get_db)],
                           user: str = Depends(get_user_from_cookie)):

    posts = await db.scalars(select(Post_moodel)
                             .where(Post_moodel.username == user, Post_moodel.is_active == True)
                             .order_by(desc('id')).limit(3))

    return templates.TemplateResponse("profile.html", {'request': request, 'username': user, 'posts': posts.all()})


@profile_router.get('/{username}')
async def get_user_profile_another(request: Request,
                                   db: Annotated[AsyncSession, Depends(get_db)],
                                   username: str = Path(min_length=4, max_length=20),
                                   user: str = Depends(get_user_from_cookie)):

    posts = await db.scalars(select(Post_moodel)
                             .where(Post_moodel.username == username,
                             Post_moodel.is_active == True)
                             .order_by(desc('id')).limit(3))

    return templates.TemplateResponse("profile.html", {'request': request, 'username': username, 'posts': posts.all()})


@profile_router.post('/logout')
async def logout_user(response: Response):
    response.delete_cookie(
        key='auth_token',
        path='/',
        samesite='lax',
        httponly=True,
        secure=True
    )
    return RedirectResponse(url="/auth/login", status_code=303)
