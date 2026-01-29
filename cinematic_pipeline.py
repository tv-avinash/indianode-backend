import sys
import subprocess
import os
import torch
import torchaudio
import librosa
import numpy as np
from audiocraft.models import MusicGen
from openai import OpenAI

# =====================================================
# CONFIG
# =====================================================

CHUNK_SEC = 8
FADE_SEC = 0.12
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

DEFAULT_PROMPT = (
    "soft musical backing track, gentle pads, light percussion, warm bass, "
    "simple rhythm, supportive background only, smooth and subtle"
)

# =====================================================
# Helpers
# =====================================================

def run(cmd):
    subprocess.run(cmd, shell=True, check=True)


def crossfade_stitch(chunks, sr):
    """Smooth stitching to avoid rhythm jumps"""
    fade = int(FADE_SEC * sr)
    final = chunks[0]

    for nxt in chunks[1:]:
        overlap1 = final[:, -fade:]
        overlap2 = nxt[:, :fade]

        fade_in = torch.linspace(0, 1, fade)
        fade_out = 1 - fade_in

        mix = overlap1 * fade_out + overlap2 * fade_in
        final = torch.cat([final[:, :-fade], mix, nxt[:, fade:]], dim=1)

    return final


# =====================================================
# AI PROMPT GENERATOR
# =====================================================

def generate_prompt_from_audio(path):
    """Analyze audio → ask LLM → get smart MusicGen prompt"""

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("⚠ No OPENAI_API_KEY found. Using default prompt.")
        return DEFAULT_PROMPT

    print("\n🧠 Analyzing audio & generating smart prompt...")

    client = OpenAI(api_key=api_key)

    y, sr = librosa.load(path, sr=22050)

    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)

    # ⭐ critical fix for numpy array bug
    tempo = float(np.mean(tempo))
    energy = float(np.mean(librosa.feature.rms(y=y)))
    brightness = float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)))

    if energy < 0.03:
        mood = "calm"
    elif energy > 0.08:
        mood = "energetic"
    else:
        mood = "medium"

    system = """
    You are a professional music producer.

    Generate ONE short MusicGen prompt for subtle background accompaniment.
    It must:
    - support vocals
    - be minimal
    - not cinematic trailer
    - not epic
    - not overpowering

    Output only the prompt text.
    """

    user = f"""
    tempo: {tempo:.1f}
    energy: {energy:.3f}
    brightness: {brightness:.1f}
    mood: {mood}

    Create a suitable backing music prompt.
    """

    res = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ]
    )

    prompt = res.choices[0].message.content.strip()

    print("🎵 Generated prompt:", prompt)
    return prompt


# =====================================================
# INPUT
# =====================================================

if len(sys.argv) < 2:
    print("Usage: python cinematic_pipeline.py input_audio")
    sys.exit(1)

input_file = sys.argv[1]


# =====================================================
# STEP 1 — Convert audio
# =====================================================

print("\n🎤 Step 1 — Converting audio...")
run(f'ffmpeg -y -i "{input_file}" -ac 1 -ar 32000 vocal.wav')


# =====================================================
# STEP 2 — Get smart prompt
# =====================================================

PROMPT = generate_prompt_from_audio("vocal.wav")


# =====================================================
# STEP 3 — Load MusicGen
# =====================================================

print("\n🎵 Loading MusicGen-large...")
model = MusicGen.get_pretrained("facebook/musicgen-large", device=DEVICE)

wav, sr = torchaudio.load("vocal.wav")

total_samples = wav.shape[1]
chunk_samples = int(CHUNK_SEC * sr)

chunks = []


# =====================================================
# STEP 4 — Generate background music
# =====================================================

print("\n🎼 Generating background music...")

for i in range(0, total_samples, chunk_samples):

    dur = min(CHUNK_SEC, (total_samples - i) / sr)

    model.set_generation_params(
        duration=dur,
        temperature=0.75,
        use_sampling=True
    )

    print(f"   chunk {i/sr:.1f}s → {i/sr+dur:.1f}s")

    music = model.generate([PROMPT])
    chunks.append(music.cpu()[0])


# =====================================================
# STEP 5 — Stitch smoothly
# =====================================================

print("\n🔧 Stitching chunks...")
bgm = crossfade_stitch(chunks, sr)

torchaudio.save("bgm.wav", bgm, 32000)


# =====================================================
# STEP 6 — Mix + Master
# =====================================================

print("\n🎚 Mixing + mastering...")

run(
    'ffmpeg -y -i vocal.wav -i bgm.wav '
    '-filter_complex "'
    'amix=inputs=2:weights=1 1.4:normalize=0,'
    'loudnorm,'
    'acompressor=threshold=-18dB:ratio=2:attack=5:release=50,'
    'volume=1.5,'
    'alimiter'
    '" final_mix.wav'
)

print("\n✅ DONE!")
print("Output → final_mix.wav")

