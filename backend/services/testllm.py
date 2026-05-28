import requests

r = requests.post(
    "http://localhost:11434/api/chat",
    json={
        "model": "llama3",
        "messages": [
            {"role": "user", "content": "Raconte moi une histoire pour enfants"}
        ],
        "stream": False
    }
)

print(r.json()["message"]["content"])