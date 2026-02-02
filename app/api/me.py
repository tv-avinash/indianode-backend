from fastapi import APIRouter, Request
from datetime import datetime
import sqlite3

router = APIRouter(prefix="/api", tags=["Auth"])


DB_PATH = "indianode.db"  # same DB you edited


def get_db_user(email: str):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    cur = conn.cursor()
    cur.execute(
        "SELECT email, name, plan, plan_expiry FROM users WHERE email = ?",
        (email,),
    )

    row = cur.fetchone()
    conn.close()

    return dict(row) if row else None


@router.get("/me")
def me(request: Request):
    session_user = request.session.get("user")

    if not session_user:
        return {"logged_in": False}

    db_user = get_db_user(session_user["email"])

    if not db_user:
        return {"logged_in": False}

    # 🔥 auto-downgrade expired plans
    if db_user["plan"] == "pro" and db_user["plan_expiry"]:
        expiry = datetime.fromisoformat(db_user["plan_expiry"])
        if expiry < datetime.utcnow():
            db_user["plan"] = "free"

    return {
        "logged_in": True,
        "email": db_user["email"],
        "name": db_user["name"],
        "plan": db_user["plan"],
        "plan_expiry": db_user["plan_expiry"],
    }

@router.post("/logout")
def logout(request: Request):
    request.session.clear()
    return {"ok": True}
