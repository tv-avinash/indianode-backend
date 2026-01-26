import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM


class SingerDecisionService:
    """
    AI-based singer decision service.
    Decides: male | female | duet
    Uses reasoning (no hardcoded rules).
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_model()
        return cls._instance

    def _load_model(self):
        print("[SingerDecisionService] Loading flan-t5-base on GPU")

        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        self.tokenizer = AutoTokenizer.from_pretrained(
            "google/flan-t5-base"
        )

        self.model = AutoModelForSeq2SeqLM.from_pretrained(
            "google/flan-t5-base",
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
        ).to(self.device)

        self.model.eval()

    def decide(
        self,
        lyrics: str,
        language: str,
        mood: str,
        style: str
    ) -> str:
        prompt = (
            "You are an expert Indian music director.\n\n"
            "Analyze the song details and decide the best vocal arrangement.\n\n"
            "Return ONLY one word:\n"
            "male\nfemale\nduet\n\n"
            f"Language: {language}\n"
            f"Mood: {mood}\n"
            f"Style: {style}\n"
            f"Lyrics:\n{lyrics}\n"
        )

        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=512
        ).to(self.device)

        with torch.no_grad():
            output = self.model.generate(
                **inputs,
                max_new_tokens=5,
                temperature=0.7
            )

        decision = self.tokenizer.decode(
            output[0],
            skip_special_tokens=True
        ).strip().lower()

        # Final safety normalization (NOT logic, just sanitation)
        if decision not in {"male", "female", "duet"}:
            decision = "male"

        return decision

