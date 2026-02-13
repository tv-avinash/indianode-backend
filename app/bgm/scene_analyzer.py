import glob
import torch
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration

device = "cuda" if torch.cuda.is_available() else "cpu"

processor = BlipProcessor.from_pretrained(
    "Salesforce/blip-image-captioning-base"
)

model = BlipForConditionalGeneration.from_pretrained(
    "Salesforce/blip-image-captioning-base"
).to(device)


def detect_scene(frames_path="frames/*.jpg", max_frames=25):
    """
    Returns AI-generated natural language description of the video.
    No labels. No hardcoding. Pure captioning.
    """

    files = sorted(glob.glob(frames_path))[:max_frames]

    captions = []

    for f in files:
        img = Image.open(f).convert("RGB")

        inputs = processor(img, return_tensors="pt").to(device)

        with torch.no_grad():
            output = model.generate(**inputs, max_new_tokens=25)

        caption = processor.decode(output[0], skip_special_tokens=True)
        captions.append(caption)

    # combine all captions
    final_caption = ". ".join(captions)

    return final_caption

