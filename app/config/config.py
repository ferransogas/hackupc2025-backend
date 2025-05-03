import os
from dotenv import load_dotenv

CONFIG = {
    'DB_HOST': "",
    'DB_NAME': "",
    'DB_USER': "",
    'DB_PASS': "",
    'DB_PORT': "",
    'GEMINI_KEY': ""
}

def load_config():
    load_dotenv()
    CONFIG['DB_HOST'] = os.getenv("DB_HOST")
    CONFIG['DB_NAME'] = os.getenv("DB_NAME")
    CONFIG['DB_USER'] = os.getenv("DB_USER")
    CONFIG['DB_PASS'] = os.getenv("DB_PASS")
    CONFIG['DB_PORT'] = os.getenv("DB_PORT")
    CONFIG['GEMINI_KEY'] = os.getenv("GEMINI_KEY")