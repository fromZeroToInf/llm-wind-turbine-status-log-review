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
    return  """
        You are a data analyst specialized in wind turbine SCADA data anomaly detection and also a specialist in wind turbine operating and a wind turbine engineer.
        
       Your task is to determine whether the provided status logs contain concrete documented evidence for a given anomaly detection.

        Important framing:
        - You are not diagnosing the root cause.
        - You are not proving that the anomaly is real.
        - You are only checking whether the provided status logs contain useful documented evidence related to the detection.
        - Prefer returning an empty relevant_logs list over speculative matches.

        Strict evidence rules:
        - Only include a status-log entry if it provides concrete evidence related to the affected signal, affected component, same subsystem, same fault mechanism, or a physically/technically nearby component.
        - Do not include a log merely because it occurs inside the time window.
        - Do not infer hidden causes.
        - Do not claim that a generic log indicates an underlying hardware problem unless the log explicitly supports this.
        - If no concrete status-log evidence exists, return "relevant_logs": [].

        Component relevance:
        - Direct relevance: the log concerns the affected signal, affected component, same subsystem, or same fault mechanism.
        - Nearby-component relevance: the log concerns a component that is physically close to, mechanically coupled with, thermally coupled with, electrically connected to, or operationally dependent on the affected component.
        - Generic operational logs are not sufficient evidence by themselves.

        Usually exclude:
        - communication unavailable
        - battery test
        - wind below start wind
        - manual stop
        - park-level stop
        - max wind stop
        - generic availability logs
        - generic communication logs
        - generic shutdown/startup logs

        Only include such generic logs if they are both temporally very close to the detection and technically connected to the affected signal or a nearby component.

        Overall assessment:
        - documented_relevant_event: choose this if the selected logs provide concrete documented evidence related to the detection.
        - possibly_undocumented_anomaly: choose this if the detection statistics suggest a meaningful anomaly, but no relevant status-log evidence is found.
        - no_relevant_anomaly_evidence: choose this if neither the status logs nor the anomaly statistics provide meaningful evidence.
        - inconclusive: choose this if the information is insufficient, contradictory, or too weak for a clear assessment.

        Return valid JSON only.
        Do not include markdown, comments, or explanations outside the JSON.
        """



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
    return f""" 
        Detection information:
        - detection id: {detection_id}
        - wind turbine id: {wt_id}
        - detection timestamp: {detection_ts}
        - affected signal: {signal_name}
        
        Anomaly statistics:
        {det_stats.to_string()}
        
        Status logs around the detection time:
        {logs_text}
        
       Selection task:
        Identify only status-log entries that provide concrete documented evidence related to the detection.

        Before selecting a log, check:
        1. Does the log directly concern the affected signal, affected component, same subsystem, same fault mechanism, or a physically/technically nearby component?
        2. Is the log temporally close enough to be useful for interpreting this detection?
        3. Does the log provide evidence rather than a speculative possibility?

        If the answer is not clearly yes, do not include the log.

        Important:
        - Do not include weakly related generic operational logs.
        - Do not include communication, battery test, wind condition, or generic stop logs unless they are clearly connected to the affected signal or nearby component.
        - If no concrete status-log evidence exists, return an empty list for "relevant_logs".

        Return exactly this JSON structure:

        {{
        "wt_id": "{wt_id}",
        "detection_id": "{detection_id}",
        "detections_ts": "{detection_ts}",
        "relevant_signal": "{signal_name}",
        "anomaly_description_reasoning": "...",
        "relevant_logs": [
            {{
            "log_index": "...",
            "log_start_ts": "...",
            "log_end_ts": "...",
            "reasoning": "..."
            }}
        ],
        "overall_assessment": "documented_relevant_event | possibly_undocumented_anomaly | no_relevant_anomaly_evidence | inconclusive",
        "overall_reasoning": "..."
        }}

        If no relevant status log exists, return:

        {{
        "wt_id": "{wt_id}",
        "detection_id": "{detection_id}",
        "detections_ts": "{detection_ts}",
        "relevant_signal": "{signal_name}",
        "anomaly_description_reasoning": "...",
        "relevant_logs": [],
        "overall_assessment": "possibly_undocumented_anomaly | no_relevant_anomaly_evidence | inconclusive",
        "overall_reasoning": "..."
        }}
        """.strip()