import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

MODEL_ID = "meta-llama/Meta-Llama-3-8B-Instruct"


class LyricsService:
    def __init__(self):
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"[LyricsService] Loading {MODEL_ID} on {device}")

        self.tokenizer = AutoTokenizer.from_pretrained(
            MODEL_ID,
            use_fast=True
        )

        self.model = AutoModelForCausalLM.from_pretrained(
            MODEL_ID,
            torch_dtype=torch.float16 if device == "cuda" else torch.float32,
            device_map="auto"
        )

    def generate(
        self,
        language: str,
        mood: str,
        theme: str,
        lines: int
    ) -> str:
        prompt = f"""
You are a professional songwriter.

Write EXACTLY {lines} lines of song lyrics.
Language: {language}
Mood: {mood}
Theme: {theme}

Rules:
- Each line on a new line
- No explanations
- No headings
- No English unless requested
"""

        inputs = self.tokenizer(
            prompt,
            return_tensors="pt"
        ).to(self.model.device)

        with torch.no_grad():
            output = self.model.generate(
                **inputs,
                max_new_tokens=300,
                temperature=0.9,
                top_p=0.95,
                do_sample=True,
                repetition_penalty=1.1,
                eos_token_id=self.tokenizer.eos_token_id
            )

        text = self.tokenizer.decode(
            output[0],
            skip_special_tokens=True
        )

        # Remove prompt from output
        lyrics = text.replace(prompt, "").strip()

        # Hard safety: enforce line count
        lines_out = [l.strip() for l in lyrics.split("\n") if l.strip()]
        if len(lines_out) > lines:
            lines_out = lines_out[:lines]
        elif len(lines_out) < lines:
            lines_out += [f"{theme}…" for _ in range(lines - len(lines_out))]

        return "\n".join(lines_out)

