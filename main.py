from fastapi import FastAPI
from app.handlers import users

app = FastAPI()
app.include_router(users.router)

import whisper
import os
from dotenv import load_dotenv

load_dotenv()
GEMINI_KEY = os.getenv('GEMINI_KEY')


model = whisper.load_model('base') 
result = model.transcribe('hackupc2025-backend/audio2.mp3', initial_prompt='Note that is possible that one or many of the following names appear: Lila, Claudia, Ferran, María, Andrés, Jhon') 
print(result['text'])

import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate

llm = ChatGoogleGenerativeAI(model='gemma-3-27b-it', google_api_key=GEMINI_KEY, temperature=0)

template = """
You are a data extraction assistant. I will give you a sentence and a list of product categories.

Your job is to identify what does pay each person and to extract a dictionary where the keys are the product names, and the values are lists of people who will pay for those products.

Return only a valid JSON like this:
{{ "pizza": ["Claudia", "Ferran"], "beverages": ["John"], "candies": ["Lila"] }}

Rules:
- Return a valid JSON dictionary.
- Keys: products.
- Values: list of people paying for the product.
- Do not include explanations.
- Respect corrections, negations and andle human messes.

Sentence: {sentence}
"""

prompt = PromptTemplate.from_template(template)
chain = prompt | llm

result = chain.invoke({'sentence': result['text']})
print(result)

