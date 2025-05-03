from app.database import database
from fastapi import APIRouter

router = APIRouter()

@router.get("/users")
def read_usuarios():
    conn = database.get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, nombre FROM usuarios")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"id": row[0], "name": row[1]} for row in rows]