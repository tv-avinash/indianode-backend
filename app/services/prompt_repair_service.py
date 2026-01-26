# app/services/prompt_repair_service.py

from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def repair_prompt(original_prompt: str, failure_reason: str) -> str:
    """
    GPT intelligently fixes the prompt WITHOUT changing intent.
    Only improves quality instructions.
    """

    print("🔧 GPT repairing prompt...")

    resp = client.chat.completions.create(
        model="gpt-4o",
        temperature=0.3,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert MusicGen prompt engineer. "
                    "Fix prompts to improve audio quality but NEVER change the user's musical intent."
                )
            },
            {
                "role": "user",
                "content": f"""
Prompt:
{original_prompt}

Audio failed because:
{failure_reason}

Rewrite the prompt to:
- improve tuning
- improve clarity
- reduce artifacts
- make it more professional

Do NOT change instruments, mood, or genre.

Return ONLY the new prompt text.
"""
            }
        ]
    )

    return resp.choices[0].message.content.strip()

