import json
from typing import Any

#TODO: if not a valid response format, then try to fix it through the llm again
def parse_to_json(response: str) -> dict[str, Any]:
    try: 
        parsed = json.loads(response)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Response is not valid JSON") from exc

    if not isinstance(parsed, dict):
        raise ValueError(f"Expected JSON object, got: {type(parsed)}")
    
    return parsed