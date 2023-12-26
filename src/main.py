#!/usr/bin/python -u
from fastapi import FastAPI

from api.routers import router


app = FastAPI(title="Авиасейлс - Поиск дешёвых авиабилетов")
app.include_router(router)
