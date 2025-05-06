import whisper
from app.config.config import CONFIG
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from app.handlers.users import get_friends
from pydantic import BaseModel, ValidationError
from typing import Dict, List
import os
import shutil
import json
import tempfile

router = APIRouter()

class ShoppingListPeople(BaseModel):
    items: Dict[str, List[str]]

@router.post("/voice")
async def process_speech(audio_file: UploadFile = File(...), products: str = Form(...), user_id: int = Form(...)):
    # Validate file type
    content_type = audio_file.content_type
    if not content_type or not content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="File must be an audio file")
    
    # create a temporary file to store the uploaded audio
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(audio_file.filename)[1]) as temp_audio:
        # copy the uploaded file content to the temporary file
        shutil.copyfileobj(audio_file.file, temp_audio)
        audio = temp_audio.name

    # parse the products
    products = json.loads(products)
        
    # get user's friends
    friends_names = get_friends_names(user_id)

    # convert the audio file to text
    text = speech_to_text(audio, friends_names)
    print(text)
    # delete the temporary file
    os.unlink(audio)

    # extract data from the transcribed text
    identified = extract_items_with_llm(text)

    # categorize the identified products
    categorized = categorize_products(identified, products.keys())

    # validate the categorized data
    return validate_data(categorized, 1).items  
    

def get_friends_names(user_id):
    return [friend['name'] for friend in get_friends(user_id)]

def speech_to_text(audio, friends):
    # load the model
    model = whisper.load_model('base')
    # transcribe the audio file knowing the user's friends and translate to english
    result = model.transcribe(audio, task="translate",
                              initial_prompt='Note that is possible that one or many of the following names appear ' + ', '.join(friends))
    print('Note that is possible that one or many of the following names appear ' + ', '.join(friends))
    return result['text']
    
def extract_items_with_llm(text: str):
    # create the data extractor llm and prompt it with the transcribed text
    llm = ChatGoogleGenerativeAI(model='gemma-3-27b-it', google_api_key=CONFIG['GEMINI_KEY'], temperature=0)

    template = """
    You are a data extraction assistant. I will give you a sentence and a list of product categories.

    Your job is to identify what does pay each person and to extract a dictionary where the keys are the product names, and the values are lists of people who will pay for those products.

    Return only a valid JSON like this:
    {{ "pizza": ["Claudia", "Ferran"], "beverages": ["Jhon"], "candies": ["Lila"] }}


    Rules:
    - Return a valid JSON dictionary.
    - Keys: products.
    - Values: list of people paying for the product.
    - Do not include explanations.
    - Do NOT include anything else: no code fences, no explanations, no extra quotation marks, no markdown, just JSON.
    - Respect corrections, negations and handle human messes.

    Sentence: {sentence}
    """

    prompt = PromptTemplate.from_template(template)
    chain = prompt | llm

    result = chain.invoke({'sentence': text})
    raw = result.content.strip()

    # clean the code in case it's markdown
    if raw.startswith("```"):
        lines = raw.splitlines()
        if lines[0].strip().lower() == "```json":
            lines = lines[1:]
        elif lines[0].strip().startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        raw = "\n".join(lines)
    
    return json.loads(raw)

def categorize_products(identified: dict, products: dict):
    # create the data extractor llm and prompt it with the transcribed text
    llm = ChatGoogleGenerativeAI(model='gemma-3-27b-it', google_api_key=CONFIG['GEMINI_KEY'], temperature=0)

    template = """
    You are a product identifier expert and you will have to categorizze them precisely.
    I will give you a dictionary A of initial products and people who pay for them, and a list B of final products.
    Your job is to categorize the initial products of the dictionary A precisely according to the products of the dictionary B.
    As a result, you will have to return a JSON dictionary with the same structure as A, but that contains just the final categorized products along with the people who pay for them.

    Return only a valid JSON like this:
    {{ "pizza": ["Claudia", "Ferran"], "towel": ["Jhon"], "popcorn": ["Lila"] }}

    Note that a initial product can be just the same as the final one, but an initial product can group some final products, or some initial products can be grouped into a final product.
    
    Rules:
    - Return a valid JSON dictionary.
    - Keys: products.
    - Values: list of people paying for the product.
    - Do not include explanations.
    - Do NOT include anything else: no code fences, no explanations, no extra quotation marks, no markdown, just JSON.
    - Respect corrections, negations and handle human messes.

    Dictionary A: {dict_a}
    List B: {list_b}
    """

    prompt = PromptTemplate.from_template(template)
    chain = prompt | llm

    result = chain.invoke({'dict_a': identified, 'list_b': products})
    raw = result.content.strip()

    # clean the code in case it's markdown
    if raw.startswith("```"):
        lines = raw.splitlines()
        if lines[0].strip().lower() == "```json":
            lines = lines[1:]
        elif lines[0].strip().startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        raw = "\n".join(lines)
    
    return json.loads(raw)

def validate_data(data: dict, num_tries: int = 0):
    # validate the struct of the data
    try:
        result = ShoppingListPeople(items=data)
        return result
    
    except ValidationError as e:
        if num_tries > 0:
            # create the data extractor llm and prompt it with the transcribed text
            llm = ChatGoogleGenerativeAI(model='gemma-3-27b-it', google_api_key=CONFIG['GEMINI_KEY'], temperature=0)

            template = """
            You are a data correction specialist. I will give you a data and an associated error and you will have to correct it so it is a valid JSON dictionary.

            Rules:
            - Return a valid JSON dictionary.
            - Keys: products.
            - Values: list of people paying for the product.
            - Do not include explanations.
            - Do NOT include anything else: no code fences, no explanations, no extra quotation marks, no markdown, just JSON.
            - Respect corrections, negations and handle human messes.

            Data: {data}
            Error: {error}
            """

            prompt = PromptTemplate.from_template(template)
            chain = prompt | llm

            result = chain.invoke({'data': data, 'error': e})
            raw = result.content.strip()

            # clean the code in case it's markdown
            if raw.startswith("```"):
                lines = raw.splitlines()
                if lines[0].strip().lower() == "```json":
                    lines = lines[1:]
                elif lines[0].strip().startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].strip().startswith("```"):
                    lines = lines[:-1]
                raw = "\n".join(lines)
            
            return validate_data(json.loads(raw))
        
        else:
            raise HTTPException(status_code=500, detail="Please try again.")
