from __future__ import annotations
from typing import Any, Protocol
import pandas as pd

class SignalContextProvider(Protocol):
    """Interface for dataset-specific signal acess
    """
    def get_detection_ts(self, detection: pd.Series)-> pd.Timestamp:
        ...
    
    def get_wt_id(self, detection: pd.Series)-> pd.Timestamp:
        ...
    
    def get_signal_name(self, detection: pd.Series) -> str:
        ...
    
    def get_signal_window(self, scada_df: pd.DataFrame, detection: pd.Series, prepost_window: int, time_unit: str) -> pd.DataFrame:
        ...
    
    def get_detection_metrics(self, detection: pd.Series) -> dict[str, Any]:
        ...
    