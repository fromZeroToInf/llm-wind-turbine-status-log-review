from __future__ import annotations
from typing import Any, Literal, Callable
import requests
from enum import StrEnum

from anthropic import Anthropic
from google import genai
from google.genai import types
from openai import OpenAI

from src.constants import MAX_TOKENS

class LLMProvider(StrEnum):
    OPENAI= "openai"
    CLAUDE= "claude"
    GEMINI= "gemini"
    OLLAMA= "ollama"


LLMCall = Callable[[str, str, str], str]

def call_llm(
    system_prompt: str,
    user_prompt: str,
    provider: LLMProvider,
    model: str,
    ) -> str:
    
   if provider not in PROVIDER_REGISTRY:
       raise ValueError(f"provider: '{provider}' not supported")
   
   return PROVIDER_REGISTRY[provider](
       system_prompt=system_prompt,
       user_prompt=user_prompt,
       model=model,
   )

def _call_ollama(
    system_prompt:str,
    user_prompt:str,
    model:str,
) -> str:
    """ Calls ollama locally. Make sure a llama model is running.
    """
    
    full_prompt = f"{system_prompt.strip()}\n\n{user_prompt.strip()}"    
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": model,
            "prompt": full_prompt,
            "stream": False,
            "format": "json",
            "options": {
                "temperature": 0.0,
            },
        },
        timeout=28800,
    )
    response.raise_for_status()
    data: dict[str, Any] = response.json()
    
    return str(data["response"])

def _call_openai(
    system_prompt:str,
    user_prompt:str,
    model:str,
) -> str:
    with OpenAI() as client:
        response = client.responses.create(
            model=model,
            instructions=system_prompt,
            input=user_prompt,
            temperature=0.0,
            text={
                "format": {"type": "json_object"}
            },
        )
    if response.output_text is None:
        raise ValueError("OpenAI returned empty content")
    
    return response.output_text

def _call_gemini(
    system_prompt:str,
    user_prompt:str,
    model:str,
) -> str:
    client = genai.Client()
    
    response = client.models.generate_content(
        model=model,
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.0,
            max_output_tokens=MAX_TOKENS,
            response_mime_type="application/json",
        ),
    )
    
    if response.text is None:
        raise ValueError("Gemini returned empty content")
    
    return response.text

def _call_claude(
    system_prompt:str,
    user_prompt:str,
    model:str,
)-> str:
    with Anthropic() as client:
        response = client.messages.create(
            model=model,
            system=system_prompt,
            message=[
                {
                    "role": "user",
                    "content": user_prompt,
                }
            ],
            temperature=0.0,
            max_tokens=MAX_TOKENS
        )
    text_blocks: list[str] = [block.text for block in response.content if block.type == "text"]
    
    if not text_blocks:
        raise ValueError("Claude returned empty content.")
    
    return "\n".join(text_blocks)

PROVIDER_REGISTRY: dict[str, LLMCall] = {
       LLMProvider.OLLAMA: _call_ollama,
       LLMProvider.OPENAI: _call_openai,
       LLMProvider.GEMINI: _call_gemini,
       LLMProvider.CLAUDE: _call_claude,
   }
 
def get_providers() -> list[str]:
    return [provider.value for provider in PROVIDER_REGISTRY]

