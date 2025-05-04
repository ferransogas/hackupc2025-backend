from app.database import database
from fastapi import APIRouter

router = APIRouter()

@router.get("/users")
def get_users():
    conn = database.get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, nombre, telefono FROM usuarios")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"id": row[0], "name": row[1], "phone": row[2]} for row in rows]

@router.get("/friends/{id}")
def get_friends(id: int):
    conn = database.get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT u.id, u.nombre, u.telefono
        FROM usuarios u, amigos a
        WHERE (u.id = a.usuario_id AND a.amigo_id = %s)
           OR (u.id = a.amigo_id AND a.usuario_id = %s);
    """, (id, id))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"id": row[0], "name": row[1], "phone": row[2]} for row in rows]