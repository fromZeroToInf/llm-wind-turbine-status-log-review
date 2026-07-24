import jsonlines
from typing import Any
import warnings
from pathlib import Path
import pandas as pd
from src import constants as cts
class llm_results:
    
    def __init__(self, path_results:Path):
        self.entries = self._load_jsonl_from_results(path_results)
    
    @classmethod
    def _load_jsonl_from_results(cls,file_path:Path)-> list[dict]:
        entries: list[dict] = []    
        try:
            with jsonlines.open(file_path, mode="r") as reader:
                for obj in reader:
                    entries.append(obj)
        except Exception as exc:
            warnings.warn(f"Error on File or Path: {exc}")
        
        return entries

    
    def get_result(self, detection_id:int) -> dict:
        return self.entries[int(detection_id)]
    
