from typing import Sequence
import pandas as pd

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

def build_prompt(detection_id: str,
                 detection_ts: pd.Timestamp,
                 wt_id: str | int,
                 signal_name: str,
                 logs_text: str,
                 det_stats: pd.DataFrame
                 ) -> str:
    cols = ["re_at_ts",
            "value_at_ts",
            "delta_at_ts",
            "z_at_ts",
            "mean_baseline",
            "std_baseline",
            "mean_event",
            "std_event",
            "delta_mean",
            "z_shift",]
    det_stats[cols] = det_stats[cols].copy().round(2)
    return f""" 
        You are a data analyst in context of wind turbine SCADA data anomaly detection and also a specialist in wind turbine operating and wind turbine engineer.
        Your Task is to identify which status-log entries may provide contextual evidence for this detection (event).
        
        Use only the provided status logs and its content.
        Do not invent causes.
        A log can be relevant even if it does not mention the signal name literally.
        Consider temporal proximity and technical plausibility (direct or indirect).
        Return valid JSON only and consider all relevant logs.
        
        Use the following statistics only as context. Do not infer a cause unless the status logs support it.
        The detection informations are:
        - detection_id: {detection_id}
        - wind turbine id: {wt_id}
        - detection timestamp: {detection_ts}
        - affected signal: {signal_name}
        - reconstruction_error_at_ts: {det_stats["re_at_ts"]}
        - value_at_detection_ts: {det_stats["value_at_ts"]}
        - delta_at_detection_ts: {det_stats["delta_at_ts"]}
        - z_at_detection_ts: {det_stats["z_at_ts"]}
        - baseline_mean: {det_stats["mean_baseline"]}
        - baseline_std: {det_stats["std_baseline"]}
        - event_mean: {det_stats["mean_event"]}
        - event_std: {det_stats["std_event"]}
        - delta_mean: {det_stats["delta_mean"]}
        - z_shift: {det_stats["z_shift"]}
        - event_window_start: {det_stats["window_start"]}
        - event_window_end: {det_stats["window_end"]}
        
        Status logs around the detection time:
        {logs_text}
        
        In the following JSON schema the log status index is the value of log_index and can be retrieved from the status logs under the name df_index and log_start_ts and log_end_ts can be retrieved from the status logs as Timestamp start and Timestamp end and at Anomaly_description_reasoning is a short, meaningful and true description of the anomaly based on the detection informations (use the statistics).
        Make sure your answer contains only the JSON and is correctly formatted and is consistent. 
        
        JSON schema:
        
        {{
            "detection_id": {detection_id},
            "detections_ts":{detection_ts},
            "relevant_signal":{signal_name},
            "Anomaly_description_reasoning": "...",
            "relevant_logs": [
                {{
                    "log_index": 1,
                    "log_start_ts": ...,
                    "log_end_ts": ...,
                    "relevance: "strong | medium | weak",
                    "reasoning": "...",
                }}
            ],
            "overall_reasoning: "..." 
        }}
        
        """.strip()