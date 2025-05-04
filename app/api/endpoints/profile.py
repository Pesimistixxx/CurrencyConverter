from fastapi import APIRouter, Depends, status, Request, Response, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, desc

from app.core.security import get_user_from_cookie
from app.api.schemas.post import CreatePost
from app.api.database.db_models import Post_moodel
from app.api.database.db_depends import get_db

profile_router = APIRouter(prefix='/profile', tags=['profile'])
templates = Jinja2Templates(directory="templates")


async def get_profile_data_post(
        text: str = Form()
) -> CreatePost:
    return CreatePost(
        text=text
    )


@profile_router.get('/', status_code=status.HTTP_200_OK, response_class=HTMLResponse)
async def get_user_profile(request: Request,
                           db: Annotated[AsyncSession, Depends(get_db)],
                           user: str = Depends(get_user_from_cookie)):
    posts = await db.scalars(select(Post_moodel)
                             .where(Post_moodel.username == user, Post_moodel.is_active == True)
                             .order_by(desc('id')).limit(3))
    return templates.TemplateResponse("profile.html", {'request': request, 'username': user, 'posts': posts.all()})


@profile_router.get('/{username}')
async def get_user_profile_another(username: str,
                                   request: Request,
                                   db: Annotated[AsyncSession, Depends(get_db)],
                                   user: str = Depends(get_user_from_cookie)):
    posts = await db.scalars(select(Post_moodel)
                             .where(Post_moodel.username == username,
                             Post_moodel.is_active == True)
                             .order_by(desc('id')).limit(3))
    return templates.TemplateResponse("profile.html", {'request': request, 'username': username, 'posts': posts.all()})


@profile_router.post('/post/create', status_code=status.HTTP_201_CREATED)
async def create_user_post(db: Annotated[AsyncSession, Depends(get_db)],
                           post_inp: CreatePost = Depends(get_profile_data_post),
                           user: str = Depends(get_user_from_cookie)):
    await db.execute(insert(Post_moodel).values(
        username=user,
        text=post_inp.text,
    ))
    await db.commit()
    return RedirectResponse('/profile', status_code=303)


@profile_router.get('/post/create')
async def create_user_get(request: Request,
                          user: str = Depends(get_user_from_cookie)
                          ):
    return templates.TemplateResponse("post_create.html", {'request': request, 'username': user})


@profile_router.get('/post/list')
async def create_user_post(request: Request,
                           db: Annotated[AsyncSession, Depends(get_db)],
                           user: str = Depends(get_user_from_cookie)):
    posts = await db.scalars(select(Post_moodel)
                             .where(Post_moodel.username == user, Post_moodel.is_active == True)
                             .order_by(desc('id')))

    return templates.TemplateResponse('post_list.html', {'request': request, 'posts': posts.all(), 'username': user})


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
