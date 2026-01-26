# app/api/kriti_midi.py

from fastapi import APIRouter
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.services.kriti_midi_service import KritiMidiService
from app.services.kriti_render_service import KritiRenderService


router = APIRouter(prefix="/api/kriti", tags=["kriti"])


# ✅ NEW schema (NO prompt anymore)
class KritiRequest(BaseModel):
    notes: str
    instrument: str = "veena"


midi_service = KritiMidiService()
render_service = KritiRenderService()


@router.post("/midi")
def create_kriti(req: KritiRequest):

    midi_path = midi_service.create_midi(
        notes=req.notes,
        instrument=req.instrument
    )

    wav_path = render_service.render(midi_path)
    return FileResponse(
        wav_path,
        media_type="audio/wav",
        filename="kriti.wav"
    )

