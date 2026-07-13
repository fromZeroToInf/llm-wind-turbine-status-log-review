from __future__ import annotations
from typing import Any
import pandas as pd

from src.signal_context_provider import SignalContextProvider

def compute_signal_context(
    scada_df: pd.DataFrame,
    detection: pd.Series,
    provider: SignalContextProvider,
    *,
    window_size: int= 24,
    time_unit: str = "hours",
) -> dict[str, Any]:
    
    signal_window = provider.get_signal_window(
        scada_df=scada_df,
        detection=detection,
        prepost_window=window_size,
        time_unit=time_unit
    )
    
    det_metrics = provider.get_detection_metrics(detection=detection)
    
    return {
        "detection_ts": str(provider.get_detection_ts(detection)),
        "wt_id": str(provider.get_wt_id(detection)),
        "signal_name": provider.get_wt_id(detection),
        "detection_metrics": det_metrics,
        "n_points": len(signal_window),
    }