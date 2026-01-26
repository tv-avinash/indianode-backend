import torch
from audiocraft.models import MusicGen
from audiocraft.data.audio import audio_write

device = "cuda" if torch.cuda.is_available() else "cpu"

model = MusicGen.get_pretrained("facebook/musicgen-large")
model.set_generation_params(
    duration=10,        # seconds
    top_k=250,
    temperature=1.0,
)

tests = {
    "hamasadwhani_violin": 
        "Indian classical instrumental music, Raga Hamsadhwani, solo violin, bright joyful mood, fast tempo, no vocals, clean studio recording",

    "kalyani_tabla": 
        "Indian classical percussion, Raga Kalyani, solo tabla rhythm, medium tempo, devotional mood, no melody instruments",

    "romantic_violin_sitar":
        "Indian classical fusion instrumental, violin and sitar duet, romantic emotional mood, slow tempo, cinematic ambience, no vocals"
}

for name, prompt in tests.items():
    print(f"Generating: {name}")
    wav = model.generate([prompt])
    audio_write(
        f"outputs/{name}",
        wav[0].cpu(),
        model.sample_rate,
        strategy="loudness",
        loudness_compressor=True
    )

print("All samples generated.")
