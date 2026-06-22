from typing import Sequence
import pandas as pd
from src import constants

def format_chunk_logs(
    chunk_log: pd.DataFrame,
    columns: Sequence[str],
    index_name: str = "df_index",
)-> str:
    missing_cols = [col for col in columns if col not in chunk_log]
    if missing_cols:
        raise ValueError(f"Missing columns: {missing_cols}")
    
    rows: list[str] = []
    
    for idx, row in chunk_log.iterrows():
        parts = [f"{index_name}={idx}"]
        for col in columns:
            value = row[col]
            parts.append(f"{col}={value}")
        
        rows.append(";".join(parts))
    
    return "\n".join(rows)

def build_system_prompt() -> str:
    return  constants.SYSTEM_PROMPT.substitute()

def build_user_prompt(
    detection_id: str,
    detection_ts: pd.Timestamp,
    wt_id: str | int,
    signal_name: str,
    logs_text: str,
    det_stats: pd.Series,
    cols_to_round: list[str] = constants.COLS_TO_ROUND
    ) -> str:
    cols = cols_to_round
    
    det_stats[cols] = det_stats[cols].copy().round(2)
    return constants.USER_PROMPT.substitute(
        detection_id=detection_id,
        detection_ts=str(detection_ts),
        wt_id=str(wt_id),
        signal_name=signal_name,
        logs_text=logs_text,
        det_stats=det_stats.to_string(),
    )