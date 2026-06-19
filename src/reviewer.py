import pandas as pd
from pathlib import Path
from typing import Any
from src import helper, llm, parser, prompt, constants

def review_detection(
    detection: pd.Series,
    log_file_path: Path,
    delta_time: pd.Timedelta,
    ts_cols: list[str],
    detection_ts_col: str,
    wt_id_col: str,
    signal_col: str,
    model: str = "llama3.2:3b",
    chunk_size: int = 30,

)-> dict[str,Any]:
    
    det_idx = detection.name
    det_ts = pd.to_datetime(detection[detection_ts_col], errors="coerce")
    wt_id = detection[wt_id_col]
    signal_name = detection[signal_col]
    
    chunks = helper.load_logfile(filePath=log_file_path,
                        detection_ts=det_ts,
                        wt_id=wt_id,
                        ts_cols=ts_cols,
                        delta_time=delta_time,
                        chunk_size=chunk_size,
                        wt_col=constants.WT_ID)
    
    
    chunks = [prompt.format_chunk_logs(chunk_log=chunk, columns=constants.LOG_COLS) for chunk in chunks]
    
    prompts = [prompt.build_prompt(detection_id=det_idx, detection_ts=det_ts, wt_id=wt_id, signal_name=signal_name, logs_text=chunk,det_stats=detection) for chunk in chunks]
    
    answers:dict[str,Any] = {}
    
    for p in prompts:
        answer = llm.call_ollama(prompt=p,
                                 model=model,
                                 temperature=0.0)
        
        answer_json = parser.parse_json(answer)
        if len(answers) == 0:
            answers = answer_json
        else:
            answers["relevant_logs"].extend(answer_json["relevant_logs"])
    
    return answers
    
    