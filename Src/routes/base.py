from fastapi import FastAPI, APIRouter,Depends
import os
from helper_function.config import get_settings ,settings

app_router = APIRouter(
      prefix= "/api",
      tags=["Base"]
)
# home of fast_api 

@app_router.get("/")
async def welcome(app_settings : settings = Depends(get_settings)): 
      app_name = app_settings.APP_NAME
      app_version  = app_settings.APP_VERSION
      return {"app_name": app_name, "app_version": app_version}

