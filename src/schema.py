from __future__ import annotations
from typing import Literal
from pydantic import BaseModel,ConfigDict, Field

class RelevantLog(BaseModel):
    model_config = ConfigDict(extra="forbid")
    log_index: str = Field(description="Original Dataframe index of the relevant status-log row")
    log_start_ts: str = Field(description="Start date of event in status-log row")
    log_end_ts: str = Field(description="End date of event in status-log row")
    reasoning: str

class LLMOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    wt_id: str
    detection_id: str = Field(description="Df index value of the detection")
    detections_ts: str = Field(description="Timestamp of the detection")
    relevant_signal: str = Field(description="Considered Signal name of the Detection")
    anomaly_description_reasoning: str = Field(description="Brief description of the anomaly event")
    relevant_logs: list[RelevantLog]
    overall_assessment: Literal[
        "documented_relevant_event",
        "possibly_undocumented_anomaly",
        "no_relevant_anomaly_evidence",
        "inconclusive"
    ]
    overall_reasoning: str
    

