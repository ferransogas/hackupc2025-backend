from app.config.config import CONFIG
import psycopg2

def get_connection():
    return psycopg2.connect(
        host=CONFIG['DB_HOST'],
        dbname=CONFIG['DB_NAME'],
        user=CONFIG['DB_USER'],
        password=CONFIG['DB_PASS'],
        port=CONFIG['DB_PORT']
    )