from typing import Any
import requests

def call_ollama(
    prompt: str,
    model: str = "llama3.2:3b",
    temperature: float = 0.0,
    timeout: int = 180,
) -> str:
    
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {
                "temperature": temperature,
            },
        },
        timeout=timeout,
    )
    
    response.raise_for_status()
    data: dict[str, Any] = response.json()
    
    return str(data["response"])