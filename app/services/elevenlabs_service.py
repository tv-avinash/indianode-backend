# app/services/elevenlabs_service.py

import os
import subprocess
from dotenv import load_dotenv
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs


# ---------------------------------------------------
# Load environment variables (.env)
# ---------------------------------------------------
load_dotenv()

ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")

if not ELEVEN_API_KEY:
    raise ValueError("ELEVEN_API_KEY not found. Please set it inside .env")


# ---------------------------------------------------
# ElevenLabs client
# ---------------------------------------------------
client = ElevenLabs(api_key=ELEVEN_API_KEY)


# ---------------------------------------------------
# Generate vocal / chant / singing track
# (Free tier safe: MP3 -> WAV via ffmpeg)
# ---------------------------------------------------
def generate_vocal(
    text: str,
    output_path: str,
    voice_id: str = "EXAVITQu4vr4xnSDxMaL",  # Bella (great for devotional/soft tone)
):
    """
    Generates a vocal/chant/singing track using ElevenLabs.

    Free plan only allows MP3 → so we:
      1. download mp3
      2. convert to wav via ffmpeg
      3. return wav path

    Args:
        text: mantra / alaap / lyrics
        output_path: final wav file path (ex: outputs/vocal.wav)
        voice_id: ElevenLabs voice id

    Returns:
        str: wav file path
    """

    # ensure wav extension
    if not output_path.endswith(".wav"):
        raise ValueError("output_path must end with .wav")

    mp3_path = output_path.replace(".wav", ".mp3")

    # --------------------------
    # Generate MP3 from ElevenLabs
    # --------------------------
    audio_stream = client.text_to_speech.convert(
        voice_id=voice_id,
        text=text,
        model_id="eleven_multilingual_v2",
        voice_settings=VoiceSettings(
            stability=0.35,          # more musical
            similarity_boost=0.7,
            style=0.8,              # expressive singing feel
            use_speaker_boost=True
        ),
        output_format="mp3_44100_128"  # ✅ free tier allowed
    )

    with open(mp3_path, "wb") as f:
        for chunk in audio_stream:
            f.write(chunk)

    # --------------------------
    # Convert MP3 -> WAV (ffmpeg)
    # --------------------------
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i", mp3_path,
            output_path
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    return output_path

