from fastapi import APIRouter
from pydantic import BaseModel
from app.services.lyrics_service import LyricsService

router = APIRouter()

lyrics_service = LyricsService()

class LyricsRequest(BaseModel):
    language: str
    mood: str
    theme: str
    lines: int = 8

class LyricsResponse(BaseModel):
    lyrics: str

@router.post("/generate-lyrics", response_model=LyricsResponse)
def generate_lyrics(req: LyricsRequest):
    lyrics = lyrics_service.generate(
        language=req.language,
        mood=req.mood,
        theme=req.theme,
        lines=req.lines
    )
    return {"lyrics": lyrics}

