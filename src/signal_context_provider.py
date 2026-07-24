from __future__ import annotations
from typing import Any, Protocol
import pandas as pd

class SignalContextProvider(Protocol):
    """Interface for dataset-specific signal access
    """
    def get_detection(self, wt_id:str, ts:str)-> pd.DataFrame:
        ...
    
    def get_scada(self, wt_id:str) -> pd.DataFrame:
        ...
    
    def get_detection_ts(self, detection: pd.DataFrame)-> pd.Timestamp:
        ...
    
    def get_wt_id(self, detection: pd.DataFrame)-> str:
        ...
    
    def get_signal_name(self, detection: pd.DataFrame) -> str:
        ...
    
    def get_signal_window(self, scada_df: pd.DataFrame, detection: pd.DataFrame) -> pd.DataFrame:
        ...
    
    def get_detection_metrics(self, detection: pd.DataFrame) -> dict[str, Any]:
        pass
    
    def get_powercurve(self) -> list:
        ...
        
    def get_data_for_pc(self, wt_id: str, window_half_size: int, det_ts:str)-> tuple[list, list]:
        ...