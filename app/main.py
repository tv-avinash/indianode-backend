# app/main.py

from fastapi import FastAPI

from app.api.generate import router as generate_router
from app.api.queue_test import router as queue_test_router
from app.api.vision import router as vision_router
from app.api.generate_from_image import router as generate_image_router
from app.api.download_mp4_image import router as download_image_router
from app.api.prompt_evaluate import router as prompt_router

app = FastAPI(
    title="Indianode AI Music API",
    version="0.3.1"
)
from app.api.kriti_midi import router as kriti_router
app.include_router(kriti_router)
app.include_router(prompt_router)
# =========================
# 🎵 Music Generation API
# =========================
app.include_router(generate_router)

# =========================
# 🖼️ Vision → Prompt API
# NOTE: prefix is ALREADY defined in vision.py
# =========================
app.include_router(vision_router)
app.include_router(generate_image_router)
app.include_router(download_image_router)

# =========================
# 🔬 Queue Test API
# =========================
app.include_router(queue_test_router)

@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "Indianode AI Music API",
        "mode": "local-test-enabled",
        "version": "0.3.1"
    }

