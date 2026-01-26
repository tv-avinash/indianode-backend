from app.services.elevenlabs_service import generate_vocal

chant = """
Om Shree Dhanvantre Namaha.
Shanti Shanti Shanti.
May the body heal,
may the breath flow,
may the mind be calm.
"""

generate_vocal(
    text=chant,
    output_path="test_voice.wav"
)

print("✅ test_voice.wav generated")

