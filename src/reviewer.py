import pandas as pd
from pathlib import Path
from typing import Any
from src import helper, llm, parser, prompt, constants
from src.llm import LLMProvider
from src.schema import LLMOutput

def review_detection(
    detection: pd.Series,
    log_file_path: Path,
    delta_time: pd.Timedelta,
    ts_cols: list[str],
    detection_ts_col: str,
    wt_id_col: str,
    signal_col: str,
    provider: LLMProvider,
    model: str = "llama3.2:3b",
    chunk_size: int = 50,

)-> LLMOutput:
    
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
    system_prompt = prompt.build_system_prompt()
    
    prompts = [prompt.build_user_prompt(detection_id=det_idx, detection_ts=det_ts, wt_id=wt_id, signal_name=signal_name, logs_text=chunk,det_stats=detection) for chunk in chunks]
    
    answers:LLMOutput | None = None
    
    for user_prompt in prompts:
        answer = llm.call_llm(
            system_prompt = system_prompt,
            user_prompt = user_prompt,
            provider=provider,
            model=model,
        )
        
        answer = parser.parse_json(answer)
        if answers is None:
            answers = answer
        else:
            answers.relevant_logs.extend(answer.relevant_logs)
    
    return answers
    
def deep_search(
    detections:pd.DataFrame,
    log_path: list[Path],
    provider: LLMProvider,
    ts_cols: list[str]= constants.TS_COLS,
    delta_time: pd.Timedelta= pd.Timedelta(days=30),
    detection_ts_col: str = constants.DET_TS_COL,
    wt_id_col: str = constants.WT_ID,
    signal_col: str = constants.SIGNAL,
    model: str = "llama3.2:3b",
    chunk_size: int = 50,
) -> list[LLMOutput]:
    
    output_list: list[LLMOutput]= []
    
    for _,row in detections.iterrows():
        wt_id = row[wt_id_col]
        log_fp = [p for p in log_path if f"_ID_{wt_id}." in p.name][0]
        
        if not log_fp:
            raise FileNotFoundError(f"Status-log file not found with wt id:{wt_id}")
        
        output = review_detection(
            detection=row,
            log_file_path=log_fp,
            delta_time=delta_time,
            ts_cols=ts_cols,
            detection_ts_col=detection_ts_col,
            wt_id_col=wt_id_col,
            signal_col=signal_col,
            provider=provider,
            model=model,
            chunk_size=chunk_size)
        
        output_list.append(output)
    
    return output_list