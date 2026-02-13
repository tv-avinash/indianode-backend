# =====================================================
# BGM TASK (DEBUG VERSION – LOUD LOGS)
# =====================================================

import os
import subprocess
import time
import uuid
from app.celery_app import celery
from app.tasks.musicgen_task import generate_music_task

FFMPEG = "/usr/bin/ffmpeg"
OUTPUT_DIR = "outputs"


# =====================================================
# helpers
# =====================================================

def run(cmd):
    print("\n🎬 FFMPEG CMD:", " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True)


def duration(path):
    print(f"\n📏 Getting duration for: {path}", flush=True)

    r = subprocess.run(
        [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            path
        ],
        capture_output=True,
        text=True
    )

    sec = int(float(r.stdout.strip()))
    print(f"⏱ Duration = {sec}s", flush=True)
    return sec


# =====================================================
# TASK
# =====================================================

@celery.task(name="bgm.generate", queue="cpu")
def generate_bgm_task(video_path: str, out_path: str, user_prompt: str = ""):

    print("\n" + "=" * 60, flush=True)
    print("🚀🚀🚀 BGM TASK RECEIVED BY CELERY 🚀🚀🚀", flush=True)
    print(f"video_path = {video_path}", flush=True)
    print(f"out_path   = {out_path}", flush=True)
    print(f"prompt     = {user_prompt}", flush=True)
    print("=" * 60 + "\n", flush=True)

    try:
        job_id = uuid.uuid4().hex[:8]
        print(f"🆔 job_id = {job_id}", flush=True)

        # -------------------------------------------------
        # duration
        # -------------------------------------------------
        sec = duration(video_path)

        prompt = (
            "Professional cinematic background score, real instruments. "
            + user_prompt
        )

        # -------------------------------------------------
        # call musicgen
        # -------------------------------------------------
        print("🎵 Sending task → musicgen.generate", flush=True)

        generate_music_task.delay(job_id, {
            "prompt": prompt,
            "duration": sec,
            "mode": "cinematic"
        })

        wav_path = os.path.join(OUTPUT_DIR, f"{job_id}.wav")
        print(f"⌛ Waiting for wav: {wav_path}", flush=True)

        # -------------------------------------------------
        # wait for wav
        # -------------------------------------------------
        wait_sec = 0
        while not os.path.exists(wav_path):
            time.sleep(1)
            wait_sec += 1

            if wait_sec % 5 == 0:
                print(f"⏳ still waiting... {wait_sec}s", flush=True)

            if wait_sec > 600:
                raise RuntimeError("❌ TIMEOUT waiting for wav!")

        if os.path.getsize(wav_path) < 10_000:
            raise RuntimeError("❌ Generated WAV is empty or invalid")

        print("✅ wav ready!", flush=True)

        # -------------------------------------------------
        # mux video + audio
        # -------------------------------------------------
        print("🎬 Muxing video + audio...", flush=True)

        run([
            FFMPEG, "-y",
            "-i", video_path,
            "-i", wav_path,
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-shortest",
            "-c:v", "copy",
            "-c:a", "aac",
            "-ar", "44100",
            "-ac", "2",
            "-b:a", "192k",
            out_path
        ])

        print("✅ FINAL VIDEO CREATED:", out_path, flush=True)
        print("🎉🎉🎉 BGM TASK DONE 🎉🎉🎉\n", flush=True)

        return out_path

    except Exception as e:
        print("\n💥💥💥 BGM TASK CRASHED 💥💥💥", flush=True)
        print(str(e), flush=True)
        raise

