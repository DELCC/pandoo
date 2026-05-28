import uuid
import httpx
from gtts import gTTS
from pathlib import Path


async def generate_story():
    async with httpx.AsyncClient(timeout=120.0) as client:
        r = await client.post(
            "http://localhost:11434/api/chat",
            json={
                "model": "llama3",
                "messages": [
                    {
                        "role": "user",
                        "content": "Raconte moi une histoire pour enfant en français"
                    }
                ],
                "stream": False
            }
        )

    story = r.json()["message"]["content"]

    BASE_DIR = Path(__file__).resolve().parent
    output_dir = BASE_DIR  / "stories_audio"
    output_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{uuid.uuid4()}.mp3"
    filepath = output_dir / filename

    tts = gTTS(text=story, lang="fr")
    tts.save(str(filepath))

    return str(filepath)


import asyncio

if __name__ == "__main__":
    filepath = asyncio.run(generate_story())
    print(f"Audio généré : {filepath}")