from fastapi import FastAPI
import uvicorn

from app.api.endpoints.users import user_router
from app.api.endpoints.profile import profile_router
from app.api.endpoints.exchanger import exchanger_router
from app.api.endpoints.posts import posts_router

app = FastAPI()


app.include_router(user_router)
app.include_router(profile_router)
app.include_router(exchanger_router)
app.include_router(posts_router)

if __name__ == '__main__':
    uvicorn.run(app, host='localhost', port=8000)
