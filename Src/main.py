from fastapi import FastAPI,APIRouter
from routes import base,data

app = FastAPI()
app.include_router(base.app_router)
app.include_router(data.data_router)