from typing import Any, Literal
from dotenv import load_dotenv
import requests
from anthropic import Anthropic
from google import genai
from openai import OpenAI

LLMProvider = Literal["openai", "claude", "gemini"]

load_dotenv()

def call_llm(
    prompt: str,
    provider: LLMProvider,
    model: str,
    temperature: float = 0.0,
    max_tokens: int = 2048,
) -> str:
    
    if provider == "openai":
        return _call_openai(system_prompt, user _)






def call_ollama(
    prompt: str,
    model: str = "llama3.2:3b",
    temperature: float = 0.0,
    timeout: int = 28800,
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