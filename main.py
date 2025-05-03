from fastapi import FastAPI
from app.handlers import users

app = FastAPI()
app.include_router(users.router)