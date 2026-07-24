from __future__ import annotations
from typing import Any
import pandas as pd

from src.signal_context_provider import SignalContextProvider

def compute_signal_context(
    wt_id: str,
    timestamp: str,
    signal: str,
    provider: SignalContextProvider,
) -> dict[str, Any]:
    
    detection = provider.get_detection(wt_id=wt_id, ts=timestamp, signal=signal)
    scada_df = provider.get_scada(wt_id=wt_id)
    
    signal_window = provider.get_signal_window(
        scada_df=scada_df,
        detection=detection,
    )
    
    det_metrics = provider.get_detection_metrics(detection=detection)
    
    return {
        "detection_ts": str(provider.get_detection_ts(detection)),
        "wt_id": str(provider.get_wt_id(detection)),
        "signal_name": provider.get_signal_name(detection),
        "detection_metrics": det_metrics if det_metrics else "",
        "n_points": len(signal_window),
        "points": signal_window,
        "window_start": str(detection["window_start"].iloc[0]),
        "window_end": str(detection["window_end"].iloc[0])
    }

def data_for_powercurve(
    wt_id: str,
    size: int,
    detection_ts: str,
    provider: SignalContextProvider,
)-> dict[str, Any]:
    data = provider.get_data_for_pc(wt_id=wt_id, window_half_size=size, det_ts=detection_ts)
    return {
        "power_curve": provider.get_powercurve(),
        "window_data": data[0],
        "detection": data[1]
    }