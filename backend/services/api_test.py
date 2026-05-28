from openai import AsyncOpenAI
import aiofiles
import asyncio
import base64
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

api_key_OPEN_AI = os.getenv("API_KEY_OPEN_AI")

clientOpenAI = AsyncOpenAI(api_key=api_key_OPEN_AI)


async def generate_story(id_child: int, voice: str = "alloy") -> str:
    try:
        # 1. Génération du texte
        response = await clientOpenAI.responses.create(
            model="gpt-4.1-mini",
            input="Génère une histoire de 10s en Français"
        )
        generated_text = response.output_text

        # 2. Génération audio via OpenAI
        audio_response = await clientOpenAI.chat.completions.create(
            model="gpt-4o-audio-preview",
            modalities=["text", "audio"],
            audio={"voice": voice, "format": "wav"},
            messages=[
                {"role": "user", "content": generated_text}
            ]
        )

        wav_bytes = base64.b64decode(audio_response.choices[0].message.audio.data)

        # 3. Sauvegarde du fichier
        BASE_DIR = Path(__file__).resolve().parent
        stories_dir = BASE_DIR / "stories_audio"
        stories_dir.mkdir(exist_ok=True)

        filename = stories_dir / f"story_{id_child}.wav"

        async with aiofiles.open(filename, "wb") as f:
            await f.write(wav_bytes)

        return str(filename)

    except Exception as e:
        raise RuntimeError(f"Erreur génération story : {e}")


asyncio.run(generate_story(2, voice="alloy"))