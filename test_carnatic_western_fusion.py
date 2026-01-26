import torch
from audiocraft.models import MusicGen
from audiocraft.data.audio import audio_write

device = "cuda" if torch.cuda.is_available() else "cpu"

model = MusicGen.get_pretrained("facebook/musicgen-large")
model.set_generation_params(
    duration=50,          # ~50 seconds
    top_k=250,
    temperature=1.1,      # allow creativity for fusion
)

prompt = (
    "Carnatic classical and Western cinematic fusion instrumental music, "
    "violin and sitar melodic lead, "
    "piano harmonic support, "
    "tabla and cinematic drums rhythm, "
    "emotional uplifting mood, "
    "medium tempo, "
    "film score style, "
    "no vocals, "
    "high quality studio recording"
)

print("Generating Carnatic + Western fusion music...")
wav = model.generate([prompt])

audio_write(
    "outputs/carnatic_western_fusion",
    wav[0].cpu(),
    model.sample_rate,
    strategy="loudness",
    loudness_compressor=True
)

print("Done. Saved to outputs/carnatic_western_fusion.wav")
