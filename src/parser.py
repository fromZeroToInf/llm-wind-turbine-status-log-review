from pydantic import ValidationError
from typing import Any
from src.schema import LLMOutput
import warnings
#TODO: if not a valid response format, then try to fix it through the llm again
def parse_json(response: str) -> LLMOutput:
    try: 
        return LLMOutput.model_validate_json(response) 
    except ValidationError as exc:
        warnings.warn(f"LLM output format is faulty")
        #TODO
        # send this response again to the llm with a new task to repair it?
        raise ValueError(f"Error: {exc}")