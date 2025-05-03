import whisper
from app.config.config import CONFIG
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from fastapi import APIRouter, File, UploadFile
import os
import shutil
import tempfile

router = APIRouter()


# TODO: relacionar els productes detectats amb els del tiquet
# TODO: usuaris del initial_prompt ha de ser una crida a la bd
@router.post("/voice")
async def process_speech(audio_file: UploadFile = File(...)):
    # create a temporary file to store the uploaded audio
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(audio_file.filename)[1]) as temp_audio:
        # copy the uploaded file content to the temporary file
        shutil.copyfileobj(audio_file.file, temp_audio)
        audio = temp_audio.name
        
    # convert the audio file to text
    # load the model
    model = whisper.load_model('base')
    # transcribe the audio file knowing the user's friends and translate to english
    result = model.transcribe(audio, task="translate", initial_prompt='Note that is possible that one or many of the following names appear: Lila, Claudia, Ferran, María, Andrés, Jhon') 

    # delete the temporary file
    os.unlink(audio)

    # create the data extractor llm and prompt it with the transcribed text
    llm = ChatGoogleGenerativeAI(model='gemma-3-27b-it', google_api_key=CONFIG['GEMINI_KEY'], temperature=0)

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
    - Respect corrections, negations and handle human messes.

    Sentence: {sentence}
    """

    prompt = PromptTemplate.from_template(template)
    chain = prompt | llm

    result = chain.invoke({'sentence': result['text']})
    
    return result.content