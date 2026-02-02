# app/api/google_auth.py

import os
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth

from app.db.database import get_db
from app.db.models import User

router = APIRouter(prefix="/auth/google", tags=["Google Auth"])

oauth = OAuth()

oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

FRONTEND_URL = os.getenv("FRONTEND_URL", "https://indianode.com")


# ---------------------------------------------------
# 1️⃣ Redirect → Google
# ---------------------------------------------------
@router.get("/login")
async def login(request: Request):
    redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")
    return await oauth.google.authorize_redirect(request, redirect_uri)


# ---------------------------------------------------
# 2️⃣ Callback → save user + session
# ---------------------------------------------------
@router.get("/callback")
async def callback(request: Request):

    token = await oauth.google.authorize_access_token(request)
    info = token["userinfo"]

    email = info["email"]
    name = info.get("name", "")

    db = next(get_db())

    # check existing
    user = db.query(User).filter(User.email == email).first()

    if not user:
        user = User(email=email, name=name)
        db.add(user)
        db.commit()
        db.refresh(user)

    # ⭐⭐⭐ STORE SESSION (THIS FIXES EVERYTHING)
    request.session["user"] = {
        "email": user.email,
        "name": user.name,
        "is_paid": user.is_paid
    }

    return RedirectResponse(f"{FRONTEND_URL}/")

