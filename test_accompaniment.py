import torch
import torchaudio
from audiocraft.models import MusicGen

INPUT = "vocal.wav"
OUTPUT = "generated_music.wav"

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

print("Loading model...")
model = MusicGen.get_pretrained("facebook/musicgen-large", device=DEVICE)

wav, sr = torchaudio.load(INPUT)

chunk_sec = 8   # ⭐ smaller = stable
chunk_samples = int(chunk_sec * sr)

prompt = (
    "cinematic orchestral background score, lush strings, soft pads, "
    "emotional movie soundtrack, ambient, background only, no vocals"
)

outputs = []

print("Generating chunks...")

for i in range(0, wav.shape[1], chunk_samples):

    dur = min(chunk_sec, (wav.shape[1] - i) / sr)

    model.set_generation_params(
        duration=dur,
        temperature=0.8,
        use_sampling=True   # ⭐ prevents silence bug
    )

    print(f"Chunk {i/sr:.1f}s → {i/sr+dur:.1f}s")

    music = model.generate([prompt])

    outputs.append(music.cpu()[0])

final = torch.cat(outputs, dim=1)

torchaudio.save(OUTPUT, final, 32000)

print("Saved generated_music.wav")

