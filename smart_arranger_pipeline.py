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
    "instruments": ["pad", "bass", "strings"],
    "density": "medium"
}

# =====================================================
# HELPERS
# =====================================================

def run(cmd):
    subprocess.run(cmd, shell=True, check=True)


# =====================================================
# SAFE GENERAL MIDI MAP
# (never crashes on weird LLM names)
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

    "drums": "Standard Kit"
}


def add_inst(name):
    name = name.lower()

    if name not in GM:
        print(f"⚠ Unknown instrument '{name}' → using pad")
        name = "pad"

    prog = pretty_midi.instrument_name_to_program(GM[name])
    return pretty_midi.Instrument(program=prog)


# =====================================================
# LLM STYLE (only instruments, NOT harmony)
# =====================================================

def get_style(tempo, energy):

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("⚠ No API key → using default style")
        return DEFAULT_STYLE

    client = OpenAI(api_key=api_key)

    prompt = f"""
    Tempo: {tempo}
    Energy: {energy}

    Choose accompaniment instruments only.

    Allowed:
    piano, bass, strings, pad, guitar, drums

    Return STRICT JSON:
    {{
      "instruments": [...],
      "density": "low|medium|high"
    }}
    """

    r = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    txt = r.choices[0].message.content.strip()

    try:
        data = json.loads(txt)

        if isinstance(data, dict):
            return data

        if isinstance(data, list):
            return {"instruments": data, "density": "medium"}

    except:
        pass

    print("⚠ LLM parse failed → default style")
    return DEFAULT_STYLE


# =====================================================
# CHORD DETECTION (harmonic intelligence)
# =====================================================

NOTE_NAMES = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']


def detect_chords(y, sr):

    print("🎼 Detecting chords from harmony...")

    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)

    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
    beat_times = librosa.frames_to_time(beats, sr=sr)

    chords = []

    for i in range(len(beats)-1):
        s = beats[i]
        e = beats[i+1]

        slice_chroma = chroma[:, s:e]
        energy = slice_chroma.mean(axis=1)

        root = np.argmax(energy)
        chords.append(NOTE_NAMES[root])

    return chords, beat_times, float(np.mean(tempo))


# =====================================================
# MIDI BUILDER (follows chords)
# =====================================================

def build_midi(chords, beat_times, tempo, style, duration):

    pm = pretty_midi.PrettyMIDI(initial_tempo=tempo)

    density_mult = {
        "low": 2,
        "medium": 1,
        "high": 0.5
    }[style["density"]]

    instruments = []

    for name in style["instruments"]:
        if name == "drums":
            inst = pretty_midi.Instrument(program=0, is_drum=True)
        else:
            inst = add_inst(name)

        instruments.append((name, inst))

    for i, chord in enumerate(chords):

        start = beat_times[i]
        end = beat_times[i+1] if i+1 < len(beat_times) else duration

        root = NOTE_NAMES.index(chord)
        root_midi = 60 + root

        for name, inst in instruments:

            if name in ["bass", "upright bass"]:
                inst.notes.append(
                    pretty_midi.Note(85, root_midi-24, start, end)
                )

            elif name in ["pad", "strings", "piano", "guitar"]:
                for p in [0, 4, 7]:
                    inst.notes.append(
                        pretty_midi.Note(55, root_midi+p, start, end)
                    )

            elif name == "drums":
                inst.notes.append(
                    pretty_midi.Note(90, 36, start, start+0.1)
                )

    for _, inst in instruments:
        pm.instruments.append(inst)

    pm.write("accompaniment.mid")


# =====================================================
# MAIN
# =====================================================

if len(sys.argv) < 2:
    print("Usage: python smart_arranger_pipeline.py input_audio")
    sys.exit(1)

input_file = sys.argv[1]

# -----------------------------------------------------

print("\n🎤 Converting audio...")
run(f'ffmpeg -y -i "{input_file}" -ac 1 -ar {SR} vocal.wav')

y, sr = librosa.load("vocal.wav", sr=22050)

energy = float(np.mean(librosa.feature.rms(y=y)))

chords, beat_times, tempo = detect_chords(y, sr)

print("Tempo:", tempo)

style = get_style(tempo, energy)
print("Style:", style)

duration = len(y)/sr

build_midi(chords, beat_times, tempo, style, duration)

# -----------------------------------------------------

print("\n🔊 Rendering instruments...")
run(f'fluidsynth -ni {SF2} accompaniment.mid -F bgm.wav -r {SR}')

print("\n🎚 Mixing...")
run(
    f'ffmpeg -y -i vocal.wav -i bgm.wav '
    f'-filter_complex "amix=inputs=2:weights=1 1.4,loudnorm" '
    f'-ar {SR} final_mix.wav'
)

print("\n✅ DONE → final_mix.wav")

