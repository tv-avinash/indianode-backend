import os
import sys
import json
import random
import subprocess
import numpy as np
import librosa
import pretty_midi
from openai import OpenAI

SR = 32000
SF2 = "FluidR3_GM.sf2"


# =====================================================
# helpers
# =====================================================

def run(cmd):
    subprocess.run(cmd, shell=True, check=True)


def jitter(t, amount=0.012):
    return t + random.uniform(-amount, amount)


def vel(base):
    return int(base + random.randint(-5, 5))


# =====================================================
# MIDI MAP
# =====================================================

GM = {
    "piano": "Acoustic Grand Piano",
    "bass": "Acoustic Bass",
    "strings": "String Ensemble 1",
    "pad": "Pad 2 (warm)",
    "guitar": "Acoustic Guitar (steel)"
}


def add_inst(name):

    name = name.lower()

    if name == "drums":
        return pretty_midi.Instrument(program=0, is_drum=True)

    if name not in GM:
        name = "pad"

    prog = pretty_midi.instrument_name_to_program(GM[name])
    return pretty_midi.Instrument(program=prog)


# =====================================================
# SAFE STYLE
# =====================================================

def get_style():

    default = {"instruments": ["pad", "bass", "strings", "drums"]}

    key = os.getenv("OPENAI_API_KEY")
    if not key:
        return default

    try:
        client = OpenAI(api_key=key)

        r = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[{
                "role": "user",
                "content": "Choose instruments only from piano,bass,pad,strings,guitar,drums. Return JSON {\"instruments\":[...]}"
            }]
        )

        parsed = json.loads(r.choices[0].message.content)

        if isinstance(parsed, dict) and "instruments" in parsed:
            return parsed

        if isinstance(parsed, list):
            return {"instruments": parsed}

    except:
        pass

    return default


# =====================================================
# harmony detection
# =====================================================

NOTE_NAMES = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']


def detect_chords(y, sr):

    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)

    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
    beat_times = librosa.frames_to_time(beats, sr=sr)

    chords = []

    for i in range(len(beats)-1):
        s, e = beats[i], beats[i+1]
        energy = chroma[:, s:e].mean(axis=1)
        root = np.argmax(energy)
        chords.append(NOTE_NAMES[root])

    return chords, beat_times, float(np.mean(tempo))


# =====================================================
# smooth dynamics
# =====================================================

def section(t, duration):

    r = t / duration

    if r < 0.25: return "intro"
    if r < 0.65: return "verse"
    if r < 0.9: return "chorus"
    return "outro"


VEL_MAP = {
    "intro": 58,
    "verse": 65,
    "chorus": 72,
    "outro": 60
}


# =====================================================
# MIDI builder
# =====================================================

def build_midi(chords, beat_times, tempo, style, duration):

    pm = pretty_midi.PrettyMIDI(initial_tempo=tempo)

    inst_objs = {name: add_inst(name) for name in style["instruments"]}

    for i, chord in enumerate(chords):

        start = beat_times[i]
        end = beat_times[i+1] if i+1 < len(beat_times) else duration

        sec = section(start, duration)
        base = VEL_MAP[sec]

        root = NOTE_NAMES.index(chord)
        root_midi = 60 + root

        for name, inst in inst_objs.items():

            if sec == "intro" and name not in ["pad"]:
                continue

            if sec == "verse" and name not in ["pad", "bass"]:
                continue

            if name == "bass":
                inst.notes.append(pretty_midi.Note(vel(base-5), root_midi-24, jitter(start), jitter(end)))

            elif name in ["pad", "strings", "piano", "guitar"]:
                for p in [0,4,7]:
                    inst.notes.append(pretty_midi.Note(vel(base-10), root_midi+p, jitter(start), jitter(end)))

            elif name == "drums":
                inst.notes.append(pretty_midi.Note(55, 36, jitter(start), jitter(start+0.07)))

    for inst in inst_objs.values():
        pm.instruments.append(inst)

    pm.write("accompaniment.mid")


# =====================================================
# MAIN
# =====================================================

if len(sys.argv) < 2:
    print("Usage: python smart_arranger_smooth_pipeline.py input_audio")
    sys.exit(1)

input_file = sys.argv[1]

print("🎤 Converting...")
run(f'ffmpeg -y -i "{input_file}" -ac 1 -ar {SR} vocal.wav')

y, sr = librosa.load("vocal.wav", sr=22050)

chords, beat_times, tempo = detect_chords(y, sr)

style = get_style()
print("Style:", style)

duration = len(y)/sr

build_midi(chords, beat_times, tempo, style, duration)

print("🔊 Rendering...")
run(f'fluidsynth -ni {SF2} accompaniment.mid -F bgm.wav -r {SR}')

print("🎚 Mixing + mastering...")

run(
    f'ffmpeg -y -i vocal.wav -i bgm.wav '
    f'-filter_complex "amix=inputs=2:weights=1 1.25,'
    f'acompressor=threshold=-22dB:ratio=2:attack=20:release=250,'
    f'volume=2.0,alimiter=limit=0.95" '
    f'-ar {SR} final_mix.wav'
)

print("\n✅ DONE → final_mix.wav (LOUD + smooth)")

