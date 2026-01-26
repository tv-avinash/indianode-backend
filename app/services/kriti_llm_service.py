# app/services/kriti_llm_service.py

import os
import json
from openai import OpenAI


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


SYSTEM_PROMPT = """
You are a Carnatic music composer.

Convert the user's request into STRICT JSON.

Rules:
- Output ONLY JSON
- No explanation text
- Use Carnatic swaras: S R G M P D N
- Separate notes with spaces
- Use | for phrase breaks
- Keep it musical and realistic
- 2–4 avartanams only (short kriti)

Return format:

{
  "tempo": 90,
  "notes": "S R G P N S | N P G R S"
}
"""


class KritiLLMService:

    def compose(self, user_prompt: str):

        res = client.chat.completions.create(
            model="gpt-4o-mini",   # fast + cheap
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
        )

        text = res.choices[0].message.content.strip()

        # force JSON parse
        data = json.loads(text)

        return data["notes"], data["tempo"]

