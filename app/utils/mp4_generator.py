# app/utils/mp4_generator.py

import subprocess
import os


def wav_to_mp4(wav_path: str, mp4_path: str, image_path: str | None = None):
    """
    Generate MP4 from WAV.
    If image_path is provided → embed image as video.
    If not → fallback to black video (Flow-1 behavior).
    """

    cmd = ["/usr/bin/ffmpeg", "-y"]

    if image_path and os.path.exists(image_path):
        # 🔥 FLOW-2: IMAGE + AUDIO
        cmd += [
            "-loop", "1",
            "-i", image_path,
            "-i", wav_path,
            "-c:v", "libx264",
            "-tune", "stillimage",
            "-pix_fmt", "yuv420p",
            "-vf", "scale=1080:1080",
            "-c:a", "aac",
            "-shortest",
            mp4_path,
        ]
    else:
        # 🟢 FLOW-1: AUDIO ONLY (BLACK VIDEO)
        cmd += [
            "-f", "lavfi",
            "-i", "color=c=black:s=1080x1080:r=30",
            "-i", wav_path,
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-shortest",
            mp4_path,
        ]

    subprocess.run(cmd, check=True)

