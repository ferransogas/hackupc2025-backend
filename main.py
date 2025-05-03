from fastapi import FastAPI
from app.handlers import users

app = FastAPI()
app.include_router(users.router)

import whisper

model = whisper.load_model("base")
result = model.transcribe("hackupc2025-backend/audio2.mp3", initial_prompt="Note that is possible that one or many of the following names appear: Lila, Claudia, Ferran, María, Andrés, Jhon")
print(result)