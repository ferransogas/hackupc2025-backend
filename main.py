from fastapi import FastAPI
from app.handlers import users
from app.handlers import voice
from app.config.config import load_config

load_config()
app = FastAPI()
app.include_router(users.router)
app.include_router(voice.router)