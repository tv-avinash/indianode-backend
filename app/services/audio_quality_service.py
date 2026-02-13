# app/services/audio_quality_service.py

def check_audio_quality(wav_path: str, prompt: str, mode: str, attempt: int = 1):
    print("⚠️ QA DISABLED — auto pass")
    return True, "skipped"

