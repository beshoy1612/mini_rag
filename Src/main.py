from fastapi import FastAPI,APIRouter
from routes import base,data
from motor.motor_asyncio import AsyncIOMotorClient
from helper_function.config import get_settings

app = FastAPI()
@app.on_event("startup")
async def startup_db_client():
    settings = get_settings()
    app.mongo_conn =  AsyncIOMotorClient(settings.MONGODB_URL)
    app.db_client = app.mongo_conn[settings.MONGODB_DATABASE]

@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongo_conn.close()

app.include_router(base.app_router)
app.include_router(data.data_router)