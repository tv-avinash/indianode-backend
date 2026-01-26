# app/services/kriti_render_service.py

import subprocess
from pathlib import Path
import uuid


BASE_DIR = Path(__file__).resolve().parents[2]

MIDI_DIR = BASE_DIR / "outputs/midi"
RENDER_DIR = BASE_DIR / "outputs/renders"

# ✅ Use absolute paths (systemd-safe)
FLUIDSYNTH_BIN = "/usr/bin/fluidsynth"
SOUNDFONT = "/usr/share/sounds/sf2/FluidR3_GM.sf2"


class KritiRenderService:

    def __init__(self):
        RENDER_DIR.mkdir(parents=True, exist_ok=True)

    # -------------------------------------------------
    # 🎯 Render MIDI → WAV using FluidSynth
    # -------------------------------------------------
    def render(self, midi_path: str) -> str:

        midi_path = str(Path(midi_path).resolve())

        if not Path(midi_path).exists():
            raise FileNotFoundError(f"MIDI missing: {midi_path}")

        if not Path(FLUIDSYNTH_BIN).exists():
            raise FileNotFoundError("fluidsynth not found at /usr/bin/fluidsynth")

        if not Path(SOUNDFONT).exists():
            raise FileNotFoundError("SoundFont missing: FluidR3_GM.sf2")

        out_file = RENDER_DIR / f"{uuid.uuid4()}.wav"

        cmd = [
            FLUIDSYNTH_BIN,   # ✅ absolute path
            "-ni",
            SOUNDFONT,
            midi_path,
            "-F", str(out_file),
            "-r", "44100"
        ]

        subprocess.run(cmd, check=True)

        return str(out_file)

