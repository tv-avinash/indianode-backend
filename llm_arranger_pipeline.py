import os
import sys
import json
import subprocess
import numpy as np
import librosa
import pretty_midi
from openai import OpenAI

# =====================================================
# CONFIG
# =====================================================

SR = 32000
SF2 = "FluidR3_GM.sf2"

DEFAULT_STYLE = {
    "instruments": ["piano", "bass", "strings"],
    "density": "low",
    "drums": False
}

# =====================================================
# HELPERS
# =====================================================

def run(cmd):
    subprocess.run(cmd, shell=True, check=True)


# =====================================================
# SAFE GENERAL MIDI MAP
# (handles ANY LLM output safely)
# =====================================================

GM = {
    "piano": "Acoustic Grand Piano",
    "keys": "Electric Piano 1",

    "bass": "Acoustic Bass",
    "upright bass": "Acoustic Bass",

    "strings": "String Ensemble 1",

    "pad": "Pad 2 (warm)",
    "ambient pad": "Pad 2 (warm)",

    "guitar": "Acoustic Guitar (steel)",
    "acoustic guitar": "Acoustic Guitar (steel)",
    "electric guitar": "Electric Guitar (clean)",

    "drums": "Standard Kit"
}


def add_instrument(name):
    name = name.lower()

    if name not in GM:
        print(f"⚠ Unknown instrument '{name}' → using piano")
        name = "piano"

    prog = pretty_midi.instrument_name_to_program(GM[name])
    return pretty_midi.Instrument(program=prog)


# =====================================================
# LLM STYLE GENERATOR
# =====================================================

def get_style_from_llm(tempo, energy):

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("⚠ No API key → using default style")
        return DEFAULT_STYLE

    print("🧠 Asking LLM for arrangement style...")

    client = OpenAI(api_key=api_key)

    mood = "calm" if energy < 0.04 else "energetic"

    system = """
    You are a professional music arranger.

    Choose accompaniment instruments for a singer.

    Only choose from:
    piano, bass, strings, guitar, pad, drums

    Rules:
    - accompaniment only
    - NO melody doubling
    - supportive
    - simple arrangement

    Output STRICT JSON:
    {
      "instruments": [...],
      "density": "low|medium|high",
      "drums": true/false
    }
    """

    user = f"""
    tempo: {tempo:.1f}
    energy: {energy:.3f}
    mood: {mood}
    """

    res = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ]
    )

    try:
        style = json.loads(res.choices[0].message.content)
        return style
    except:
        print("⚠ LLM parse failed → default style")
        return DEFAULT_STYLE


# =====================================================
# MAIN
# =====================================================

if len(sys.argv) < 2:
    print("Usage: python llm_arranger_pipeline.py input_audio")
    sys.exit(1)

input_file = sys.argv[1]


# -----------------------------------------------------
# Step 1 — Convert audio
# -----------------------------------------------------

print("\n🎤 Converting input audio...")
run(f'ffmpeg -y -i "{input_file}" -ac 1 -ar {SR} vocal.wav')


# -----------------------------------------------------
# Step 2 — Analyze tempo + energy
# -----------------------------------------------------

print("\n🔍 Analyzing audio...")

y, sr = librosa.load("vocal.wav", sr=22050)

tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
tempo = float(np.mean(tempo))

energy = float(np.mean(librosa.feature.rms(y=y)))

print("Tempo:", tempo)
print("Energy:", energy)


# -----------------------------------------------------
# Step 3 — LLM chooses style
# -----------------------------------------------------

style = get_style_from_llm(tempo, energy)
print("🎼 Style chosen:", style)


# -----------------------------------------------------
# Step 4 — Create MIDI accompaniment
# -----------------------------------------------------

print("\n🎹 Generating accompaniment...")

pm = pretty_midi.PrettyMIDI(initial_tempo=tempo)

duration = len(y) / sr
beat_len = 60 / tempo

density_mult = {
    "low": 2,
    "medium": 1,
    "high": 0.5
}[style["density"]]


for name in style["instruments"]:

    if name == "drums":
        inst = pretty_midi.Instrument(program=0, is_drum=True)
    else:
        inst = add_instrument(name)

    t = 0

    while t < duration:

        # Bass groove
        if name in ["bass", "upright bass"]:
            inst.notes.append(
                pretty_midi.Note(80, 48, t, t + beat_len)
            )

        # Chord instruments
        elif name in ["piano", "strings", "pad", "guitar"]:
            for p in [60, 64, 67]:  # simple C chord
                inst.notes.append(
                    pretty_midi.Note(60, p, t, t + beat_len * 2)
                )

        # Drums
        elif name == "drums":
            inst.notes.append(
                pretty_midi.Note(90, 36, t, t + 0.1)
            )

        t += beat_len * density_mult

    pm.instruments.append(inst)


pm.write("accompaniment.mid")


# -----------------------------------------------------
# Step 5 — Render with fluidsynth
# -----------------------------------------------------

print("\n🔊 Rendering instruments...")
run(f'fluidsynth -ni {SF2} accompaniment.mid -F bgm.wav -r {SR}')


# -----------------------------------------------------
# Step 6 — Mix cleanly
# -----------------------------------------------------

print("\n🎚 Mixing + mastering...")

run(
    f'ffmpeg -y -i vocal.wav -i bgm.wav '
    f'-filter_complex "amix=inputs=2:weights=1 1.4:normalize=0,loudnorm,volume=1.4" '
    f'-ar {SR} final_mix.wav'
)

print("\n✅ DONE → final_mix.wav")

