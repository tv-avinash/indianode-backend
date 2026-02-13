from fastapi import APIRouter
from pydantic import BaseModel

from app.services.art_proxy import generate_art_from_mood

router = APIRouter()


# ======================================================
# REQUEST MODEL
# ======================================================

class MoodRequest(BaseModel):
    mood: str


# ======================================================
# ROUTE
# ======================================================

@router.post("/abstract-art")
def create_abstract_art(req: MoodRequest):
    """
    3090 → GPT prompt → 4090 GPU → image/music
    """
    return generate_art_from_mood(req.mood)

