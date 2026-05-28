import httpx

async def check_ollama():
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get("http://localhost:11434/api/tags")
            print(r.status_code)
            print(r.json())
    except Exception as e:
        print("Ollama indisponible:", e)


import asyncio

if __name__ == "__main__":
    filepath = asyncio.run(generate_story())
    print(f"Audio généré : {filepath}")