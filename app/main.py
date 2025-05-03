from fastapi import FastAPI
from app.handlers import users, voice, image
from app.config.config import load_config

load_config()
app = FastAPI()
app.include_router(users.router)
app.include_router(voice.router)
app.include_router(image.router)