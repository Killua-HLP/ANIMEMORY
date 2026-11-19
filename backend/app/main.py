from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db
from app.routers.auth import router as authrouter
from app.routers.user import router as user_router
from app.routers.anime import router as anime_router

app = FastAPI(title=settings.APP_NAME)

app.include_router(authrouter)
app.include_router(user_router)
app.include_router(anime_router)

@app.get("/home")
async def get_home():
    return {"message": "Welcome to AnimeMory"}

@app.get("/db-test")
async def db_test(db:Session = Depends(get_db)):
    return {"message": "Testing the Database"}

print(settings.APP_NAME)
print(settings.DEBUG)