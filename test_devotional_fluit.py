import torch
from audiocraft.models import MusicGen
from audiocraft.data.audio import audio_write

device = "cuda" if torch.cuda.is_available() else "cpu"

model = MusicGen.get_pretrained("facebook/musicgen-large")
model.set_generation_params(
    duration=60,          # 1 minute
    top_k=250,
    temperature=0.9,      # slightly controlled, devotional feel
)

prompt = (
    "Indian classical devotional instrumental music, "
    "slow tempo, peaceful spiritual mood, "
    "bansuri flute lead melody, "
    "soft tabla accompaniment, "
    "tanpura drone in background, "
    "meditative atmosphere, "
    "no vocals, clean studio recording"
)

print("Generating devotional flute + tabla music...")
wav = model.generate([prompt])

audio_write(
    "outputs/devotional_flute_tabla_60s",
    wav[0].cpu(),
    model.sample_rate,
    strategy="loudness",
    loudness_compressor=True
)

print("Done. Saved to outputs/devotional_flute_tabla_60s.wav")

