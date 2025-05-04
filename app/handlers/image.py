from fastapi import APIRouter, File, UploadFile, HTTPException
import shutil
import tempfile
import os
from PIL import Image
import pytesseract
import json
from app.config.config import CONFIG
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from pydantic import BaseModel, ValidationError
from typing import Dict, List


router = APIRouter()

class ShoppingListPrices(BaseModel):
    items: Dict[str, float]

@router.post("/image")
async def process_image(image_file: UploadFile = File(...)):
    # validate file type
    content_type = image_file.content_type
    if not content_type or not content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # create a temporary file to store the uploaded image
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(image_file.filename)[1]) as temp_image:
        # copy the uploaded file content to the temporary file
        shutil.copyfileobj(image_file.file, temp_image)
        image = temp_image.name

    # extract the text from the image
    text = image_to_string(image)

    # delete the temporary file
    os.unlink(image)

    extracted = extract_items_with_llm(text)

    return validate_data(extracted, 1)

def image_to_string(path):
    return pytesseract.image_to_string(Image.open(path))

def extract_items_with_llm(text: str) -> dict:
    llm = ChatGoogleGenerativeAI(
        model='gemma-3-27b-it',
        google_api_key=CONFIG['GEMINI_KEY'],
        temperature=0
    )
    template = """
    You are a data extraction assistant. I will give you the raw text of a purchase receipt.

    Your job is to identify each product on the receipt and extract a JSON dictionary where the keys are the product names and the values are their corresponding prices.

    Return only a valid JSON object like this:
    {{  
    "product1": "price1",  
    "product2": "price2"
    }}

    Rules:
    - The keys (products) must match exactly how they appear in the OCR text, as strings.
    - The values must be doubles: the total sum of all occurrences of each product, rounded to two decimal places.
    - If a product appears multiple times, add up its prices before converting to a double. Example: '1 Coca Cola 1.50' and then '1 Coca Cola 1.50' = 'Coca Cola': 3.00
    - Ignore irrelevant lines like totals, taxes, discounts or zero quantities.
    - Do NOT include anything else: no code fences, no explanations, no extra quotation marks, no markdown, just JSON.
    - Do not include currency symbols.
    - Return only the JSON object.

    Receipt text:
    {text}
    """
    prompt = PromptTemplate.from_template(template)
    chain = prompt | llm
    result = chain.invoke({'text': text})
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
        result = ShoppingListPrices(items=data)
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