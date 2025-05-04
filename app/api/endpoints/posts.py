from fastapi.templating import Jinja2Templates
from fastapi import APIRouter, status, Depends, Request, HTTPException, Path, Form
from fastapi.responses import RedirectResponse
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, desc

from app.api.database.db_depends import get_db
from app.api.schemas.post import CreatePost
from app.core.security import get_user_from_cookie
from app.api.database.db_models import Post_moodel

posts_router = APIRouter(prefix='/post', tags=['profile'])
templates = Jinja2Templates(directory="templates")


async def get_profile_data_post(
        text: str = Form()
) -> CreatePost:
    return CreatePost(
        text=text
    )


@posts_router.post('/create', status_code=status.HTTP_201_CREATED)
async def create_user_post(db: Annotated[AsyncSession, Depends(get_db)],
                           post_inp: CreatePost = Depends(get_profile_data_post),
                           user: str = Depends(get_user_from_cookie)):
    await db.execute(insert(Post_moodel).values(
        username=user,
        text=post_inp.text,
    ))
    await db.commit()
    return RedirectResponse('/profile', status_code=303)


@posts_router.get('/create')
async def create_user_get(request: Request,
                          user: str = Depends(get_user_from_cookie)
                          ):
    return templates.TemplateResponse("post_create.html", {'request': request, 'username': user})


@posts_router.get('/list')
async def create_user_post(request: Request,
                           db: Annotated[AsyncSession, Depends(get_db)],
                           user: str = Depends(get_user_from_cookie)):
    posts = await db.scalars(select(Post_moodel)
                             .where(Post_moodel.username == user, Post_moodel.is_active == True)
                             .order_by(desc('id')))

    return templates.TemplateResponse('post_list.html', {'request': request, 'posts': posts.all(), 'username': user})


@posts_router.get('/{post_id}')
async def get_post(request: Request,
                   db: Annotated[AsyncSession, Depends(get_db)],
                   user: str = Depends(get_user_from_cookie),
                   post_id: int = Path(ge=1)):
    post = await db.scalar(select(Post_moodel)
                     .where(Post_moodel.id == post_id))
    if post.username != user and post.is_active == False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="you aren't allowed to this post"
        )
    return post


@posts_router.delete('/{post_id}')
async def delete_post(db: Annotated[AsyncSession, Depends(get_db)],
                      user: str = Depends(get_user_from_cookie),
                      post_id: int = Path(ge=1)):
    post = await db.scalar(select(Post_moodel)
                           .where(Post_moodel.id == post_id))
    if post.username != user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="you aren't allowed to delete this post"
        )
    post.is_active = False
    await db.commit()
    return RedirectResponse('/profile', status_code=303)