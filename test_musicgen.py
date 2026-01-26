import torch
from audiocraft.models import MusicGen

device = "cuda" if torch.cuda.is_available() else "cpu"
model = MusicGen.get_pretrained("facebook/musicgen-large")
model.set_generation_params(duration=10)

wav = model.generate([
    "Indian classical instrumental music, calm mood, tanpura, bansuri"
])

print("Generated:", len(wav))
