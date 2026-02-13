# app/main.py

from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

# ✅ DB
from app.db.database import engine, Base

# ✅ routers
from app.api.generate import router as generate_router
from app.api.queue_test import router as queue_test_router
from app.api.vision import router as vision_router
from app.api.generate_from_image import router as generate_image_router
from app.api.download_mp4_image import router as download_image_router
from app.api.prompt_evaluate import router as prompt_router
from app.api.google_auth import router as google_auth_router

from app.api.kriti_midi import router as kriti_router
from app.api import accompaniment
from app.api import bgm
from app.api.me import router as me_router
from app.api.logout import router as logout_router
from app.routes import billing, razorpay_webhook
#from app.routes import billing
from app.api.abstract_api import router as abstract_router
import app.bgm.bgm_tasks   # ✅ REGISTER CELERY TASKS

# =====================================================
# App
# =====================================================

app = FastAPI(
    title="Indianode AI Music API",
    version="0.3.1"
)

app.add_middleware(
    SessionMiddleware,
    secret_key="indianode-super-secret-123"
)
app.include_router(me_router)
app.include_router(logout_router)
app.include_router(billing.router)
app.include_router(razorpay_webhook.router)
app.include_router(abstract_router, prefix="/api")
# =====================================================
# ✅ Create DB tables automatically
# =====================================================

Base.metadata.create_all(bind=engine)


# =====================================================
# Routes
# =====================================================

app.include_router(google_auth_router)
app.include_router(prompt_router)
app.include_router(kriti_router)
app.include_router(accompaniment.router)
app.include_router(bgm.router)
app.include_router(generate_router)
app.include_router(vision_router)
app.include_router(generate_image_router)
app.include_router(download_image_router)
app.include_router(queue_test_router)


# =====================================================
# Root
# =====================================================

@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "Indianode AI Music API",
        "version": "0.3.1"
    }

