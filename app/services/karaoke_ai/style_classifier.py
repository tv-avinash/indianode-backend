# app/services/karaoke_ai/style_classifier.py

import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class StyleClassifier:
    """
    Uses LLM reasoning to classify singing style
    """

    def classify(self, features: dict) -> str:
        prompt = f"""
You are an expert musicologist.

Classify the singing style based on these vocal features.

Features:
{features}

Choose ONLY one label:
carnatic
hindustani
film
western_pop
devotional
rap
ambient

Return only the label.
"""

        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        return res.choices[0].message.content.strip()

