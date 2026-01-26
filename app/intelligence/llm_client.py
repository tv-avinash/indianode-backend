# app/intelligence/llm_client.py

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

import os


ENABLE_LLM = os.getenv("ENABLE_LLM", "false") == "true"

def run_llm(prompt: str) -> str:
    if not ENABLE_LLM:
        raise RuntimeError(
            "LLM is disabled. ENABLE_LLM=true is required to use run_llm()."
        )

    # existing model loading + inference code here


MODEL_NAME = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

_tokenizer = None
_model = None
_device = None


def _load_model():
    global _tokenizer, _model, _device

    if _model is not None:
        return

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA not available – GPU required")

    _device = torch.device("cuda:0")

    print("[LLM] Loading tokenizer...")
    _tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    print("[LLM] Loading model on GPU (FP16)...")
    _model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        torch_dtype=torch.float16,
    ).to(_device)

    _model.eval()

    print(f"[LLM] Model loaded on {torch.cuda.get_device_name(0)}")


def run_llm(prompt: str) -> str:
    _load_model()

    inputs = _tokenizer(
        prompt,
        return_tensors="pt"
    )

    # 🔥 MOVE INPUTS TO GPU
    inputs = {k: v.to(_device) for k, v in inputs.items()}

    with torch.no_grad():
        output = _model.generate(
            **inputs,
            max_new_tokens=128,
            do_sample=False,
            use_cache=True,
        )

    return _tokenizer.decode(
        output[0],
        skip_special_tokens=True
    )

