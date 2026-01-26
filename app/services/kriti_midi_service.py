# app/services/kriti_midi_service.py

from mido import Message, MidiFile, MidiTrack, MetaMessage
from pathlib import Path
import uuid


BASE_DIR = Path(__file__).resolve().parents[2]
OUT_DIR = BASE_DIR / "outputs/midi"


# -------------------------------------------------------
# 🎹 General MIDI programs (FluidSynth compatible)
# -------------------------------------------------------
GM_PROGRAMS = {
    "piano": 0,
    "violin": 40,
    "flute": 73,
    "sitar": 104,
    "veena": 104,   # closest match in GM
}


# -------------------------------------------------------
# 🎵 Carnatic swara → MIDI pitch
# (C major base, you can later shift tonic)
# -------------------------------------------------------
SWARA_MAP = {
    "S": 60,  # C
    "R": 62,
    "G": 64,
    "M": 65,
    "P": 67,
    "D": 69,
    "N": 71,
}


# -------------------------------------------------------
# 🎼 Kriti MIDI Builder
# -------------------------------------------------------
class KritiMidiService:

    def __init__(self):
        OUT_DIR.mkdir(parents=True, exist_ok=True)

    # ---------------------------------------------------
    # Create MIDI from swaras
    # ---------------------------------------------------
    def create_midi(
        self,
        notes: str,
        instrument: str = "veena",
        tempo_bpm: int = 90
    ) -> str:

        # better musical resolution
        mid = MidiFile(ticks_per_beat=480)

        track = MidiTrack()
        mid.tracks.append(track)

        # ----------------------------
        # 🎯 tempo (important for feel)
        # ----------------------------
        tempo = int(60_000_000 / tempo_bpm)
        track.append(MetaMessage('set_tempo', tempo=tempo, time=0))

        # ----------------------------
        # 🎯 instrument selection
        # THIS is what fixes piano issue
        # ----------------------------
        program = GM_PROGRAMS.get(instrument.lower(), 104)
        track.append(Message('program_change', program=program, time=0))

        # ----------------------------
        # 🎯 note rendering
        # ----------------------------
        beat = 480
        note_length = int(beat * 0.9)   # legato feel (less robotic)
        gap = int(beat * 0.1)

        first_note = True

        for token in notes.split():

            if token == "|":
                continue

            pitch = SWARA_MAP.get(token.upper(), 60)

            # first note should start immediately
            start_time = 0 if first_note else gap
            first_note = False

            track.append(Message('note_on', note=pitch, velocity=90, time=start_time))
            track.append(Message('note_off', note=pitch, velocity=80, time=note_length))

        # ----------------------------
        # save
        # ----------------------------
        out_file = OUT_DIR / f"{uuid.uuid4()}.mid"
        mid.save(out_file)

        return str(out_file)

