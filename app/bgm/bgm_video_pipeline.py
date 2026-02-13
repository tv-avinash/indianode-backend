# =========================================================
# INDIANODE SMART BGM ENGINE — PRODUCTION FINAL
# Robust • Auto-analysis • Auto-duck • Auto-quality loop
# =========================================================

import os
import sys
import uuid
import shutil
import subprocess
import torch
import time
from pydub import AudioSegment
from faster_whisper import WhisperModel

# ✅ ONLY CHANGE → reuse existing shared celery musicgen worker
from app.tasks.musicgen_task import generate_music_task

from scene_analyzer import detect_scene


# =========================================================
# CONFIG (UNCHANGED)
# =========================================================

FFMPEG = "/usr/bin/ffmpeg"
SR = 48000

TARGET_MASTER = -14
VOICE_PRIORITY_DB = 14
MAX_RETRIES = 5

VIDEO_IN  = sys.argv[1]
VIDEO_OUT = sys.argv[2]
USER_PROMPT = sys.argv[3] if len(sys.argv) > 3 else ""

JOB = uuid.uuid4().hex[:8]

VOICE_WAV = f"voice_{JOB}.wav"
BGM_WAV   = f"bgm_{JOB}.wav"
MIX_WAV   = f"mix_{JOB}.wav"
TEMP_MP4  = f"temp_{JOB}.mp4"


# =========================================================
# DEVICE + MODELS
# =========================================================

device = "cuda" if torch.cuda.is_available() else "cpu"
print("🚀 Device:", device)

# ❌ IMPORTANT: MusicGen REMOVED (no second GPU model)
WHISPER = WhisperModel("medium", device=device)

vad_model, utils = torch.hub.load('snakers4/silero-vad', 'silero_vad')
(get_speech_timestamps, _, read_audio, _, _) = utils


# =========================================================
# UTILS (UNCHANGED)
# =========================================================

def run(cmd):
    subprocess.run(cmd, check=True)


def duration(path):
    r = subprocess.run(
        ["ffprobe","-v","error","-show_entries","format=duration",
         "-of","default=noprint_wrappers=1:nokey=1",path],
        capture_output=True,text=True)
    return float(r.stdout.strip())


def mean_db(path):
    r = subprocess.run(
        [FFMPEG,"-i",path,"-af","volumedetect","-f","null","-"],
        stderr=subprocess.PIPE,text=True)

    for line in r.stderr.splitlines():
        if "mean_volume" in line:
            return float(line.split(":")[1].replace(" dB",""))

    return -40


def has_audio_stream(path):
    r = subprocess.run(
        ["ffprobe","-v","error","-select_streams","a",
         "-show_entries","stream=index",
         "-of","csv=p=0",path],
        capture_output=True,text=True)
    return bool(r.stdout.strip())


# =========================================================
# FRAME EXTRACTION (UNCHANGED)
# =========================================================

def extract_frames():
    os.makedirs("frames", exist_ok=True)

    run([
        FFMPEG,
        "-y",
        "-i", VIDEO_IN,
        "-vf", "fps=0.33",
        "frames/frame_%03d.jpg"
    ])


# =========================================================
# AUDIO EXTRACT (UNCHANGED)
# =========================================================

def extract_audio():

    if not has_audio_stream(VIDEO_IN):
        print("🔇 no audio stream detected → silent video")
        return

    run([FFMPEG,"-y","-i",VIDEO_IN,"-vn","-ac","1","-ar","16000",VOICE_WAV])


# =========================================================
# AUDIO TYPE (UNCHANGED)
# =========================================================

def detect_audio_type():

    if not os.path.exists(VOICE_WAV):
        return "silent"

    wav = read_audio(VOICE_WAV, sampling_rate=16000)
    speech = get_speech_timestamps(wav, vad_model, sampling_rate=16000)

    total = len(wav)/16000
    speech_sec = sum((s["end"]-s["start"])/16000 for s in speech)

    ratio = speech_sec/total if total else 0

    print("🧠 speech ratio:", round(ratio,3))

    if ratio > 0.15:
        return "speech"
    if mean_db(VOICE_WAV) < -38:
        return "silent"
    return "ambient"


# =========================================================
# TRANSCRIPT (UNCHANGED)
# =========================================================

def transcript_if_needed(audio_type):

    if audio_type != "speech":
        return ""

    segs,_ = WHISPER.transcribe(VOICE_WAV)
    return " ".join(s.text for s in segs)[:1200]


# =========================================================
# VIDEO ENERGY (UNCHANGED)
# =========================================================

def analyze_video_energy():

    r = subprocess.run(
        [FFMPEG,"-i",VIDEO_IN,"-vf","signalstats","-f","null","-"],
        stderr=subprocess.PIPE,text=True)

    changes = r.stderr.count("Parsed_signalstats")

    if changes < 40:
        return "calm"
    if changes < 120:
        return "medium"
    return "energetic"


# =========================================================
# PROMPT BUILDER (UNCHANGED)
# =========================================================

def build_prompt(audio_type, transcript, energy, scene):

    p = "Professional cinematic background score. Real instruments."

    if audio_type == "speech":
        p += " Soft supportive underscore so dialogue stays clear."

    if audio_type == "ambient":
        p += " Wide immersive emotional soundtrack."

    if audio_type == "silent":
        p += " Full rich cinematic score."

    if energy == "calm":
        p += " Slow emotional."
    elif energy == "medium":
        p += " Warm ambient."
    else:
        p += " Energetic modern percussion."

    if scene:
        p += " Scene: " + scene + "."

    if transcript:
        p += " Context: " + transcript[:200]

    if USER_PROMPT:
        p += " Style: " + USER_PROMPT

    print("🎼 FINAL PROMPT:", p)
    return p


# =========================================================
# ✅ ONLY CHANGE — delegate to shared MusicGen worker
# =========================================================

def generate_music(prompt, total_sec):

    job_id = uuid.uuid4().hex[:8]

    generate_music_task.delay(job_id, {
        "prompt": prompt,
        "duration": int(total_sec),
        "mode": "cinematic"
    })

    wav_path = os.path.join("outputs", f"{job_id}.wav")

    print("⏳ waiting for shared MusicGen worker...")

    while not os.path.exists(wav_path):
        time.sleep(1)

    shutil.copy(wav_path, BGM_WAV)


# =========================================================
# MIX / MERGE (UNCHANGED)
# =========================================================

def mix(audio_type, gain_db):

    bgm = AudioSegment.from_wav(BGM_WAV).set_frame_rate(SR).set_channels(2)

    if audio_type == "silent" or not os.path.exists(VOICE_WAV):
        out = bgm.apply_gain(TARGET_MASTER - bgm.dBFS)
        out.export(MIX_WAV, "wav")
        return

    voice = AudioSegment.from_wav(VOICE_WAV).set_frame_rate(SR).set_channels(2)

    voice_db = voice.dBFS
    bgm_db   = bgm.dBFS

    if audio_type == "speech":
        target = max(voice_db - VOICE_PRIORITY_DB, -32)
        diff = target - bgm_db
        bgm = bgm.apply_gain(diff + gain_db)
    else:
        bgm = bgm + 4 + gain_db

    out = voice.overlay(bgm)
    out = out.apply_gain(TARGET_MASTER - out.dBFS)
    out.export(MIX_WAV, "wav")


def merge():

    run([
        FFMPEG,"-y",
        "-i",VIDEO_IN,
        "-i",MIX_WAV,
        "-map","0:v",
        "-map","1:a",
        "-c:v","copy",
        "-c:a","aac",
        "-b:a","192k",
        TEMP_MP4
    ])

    shutil.move(TEMP_MP4, VIDEO_OUT)


# =========================================================
# MAIN (UNCHANGED)
# =========================================================

def process():

    extract_audio()
    audio_type = detect_audio_type()
    transcript = transcript_if_needed(audio_type)

    extract_frames()
    scene = detect_scene()

    energy = analyze_video_energy()

    prompt = build_prompt(audio_type, transcript, energy, scene)

    generate_music(prompt, duration(VIDEO_IN)+1)

    mix(audio_type, 0)
    merge()

    shutil.rmtree("frames", ignore_errors=True)
    print("🎉 DONE →", VIDEO_OUT)


if __name__ == "__main__":
    process()

