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
                 ) -> str:
    return f""" 
        You are a data analyst in context of wind turbine SCADA data anomaly detection and also a specialist in wind turbine operating and wind turbine engineer.
        Your Task is to identify which status-log entries may provide contextual evidence for this detection (event).
        
        Use only the provided status logs and its content.
        Do not invent causes.
        A log can be relevant even if it does not mention the signal name literally.
        Consider temporal proximity and technical plausibility (direct or indirect).
        Return valid JSON only.
        
        The detection informations are:
        - detection_id: {detection_id}
        - wind turbine id: {wt_id}
        - detection timestamp: {detection_ts}
        - affected signal: {signal_name}
        
        Status logs around the detection time:
        {logs_text}
        
        JSON schema:
        
        {{
            "detection_id": "{detection_id},
            "relevant_logs": [
                {{
                    "log_index": 1,
                    "relevance: "strong | medium | weak",
                    "reasoning": "..."
                }}
            ],
            "overall_reasoning: "..." 
        }}
        """.strip()
