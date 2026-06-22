import pandas as pd
import jsonlines
import os
from pathlib import Path
from typing import Any
from src import helper, llm, parser, prompt
from src.llm import LLMProvider
from src.schema import LLMOutput
from src import constants as cts
import warnings
import time
import random as rnd


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
                        wt_col=cts.WT_ID)
    
    
    chunks = [prompt.format_chunk_logs(chunk_log=chunk, columns=cts.LOG_COLS) for chunk in chunks]
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

def _write_jsonl(file_path:Path, obj:dict, mode:str)-> None:
    with jsonlines.open(file_path, mode=mode) as writer:
            writer.write(obj)

def _get_idx(file_path:Path)-> int:
    
    last_idx: int = -1
    if file_path.exists():
        with jsonlines.open(file_path) as reader:
            row = next(iter(reader), None)
            if row is not None:
                last_idx = int(row["idx"])
    else:
        _write_jsonl(file_path, {"idx": 0}, mode="w")
        last_idx = 0
    return last_idx
            
def _all_results(file_path: Path) -> list[dict]:
    results:list[dict] = []
    if file_path.exists():
        with jsonlines.open(file_path, mode="r") as reader:
            for obj in reader:
                results.append(LLMOutput.model_validate(obj))
    return results

def deep_search(
    detections:pd.DataFrame,
    log_path: list[Path],
    provider: LLMProvider,
    ts_cols: list[str]= cts.TS_COLS,
    delta_time: pd.Timedelta= pd.Timedelta(days=30),
    detection_ts_col: str = cts.DET_TS_COL,
    wt_id_col: str = cts.WT_ID,
    signal_col: str = cts.SIGNAL,
    model: str = "llama3.2:3b",
    chunk_size: int = 50,
    max_retries: int = 3,
    wait_seconds: float = 30.0,
) -> list[LLMOutput]:
    
    wait_seconds = wait_seconds
    
    detections= detections.reset_index()
    
    cts.PATH_OUTPUT.mkdir(parents=True, exist_ok=True)
    output_file_path  = cts.PATH_OUTPUT / cts.FN_OUTPUT
    
    cts.PATH_LAST_IDX.mkdir(parents=True, exist_ok=True)
    idx_path = cts.PATH_LAST_IDX / cts.FN_IDX
    
    last_idx = _get_idx(idx_path)
    
    for idx,row in detections.iterrows():
        
        if idx < last_idx:
            continue
        attempts= 0
        
        while attempts <= max_retries:
            try:
                wt_id = row[wt_id_col]
                
                matching_file = [p for p in log_path if f"_ID_{wt_id}." in p.name][0]
                
                if not matching_file:
                    raise FileNotFoundError(f"Status-log file not found with wt id:{wt_id}")
                
                output = review_detection(
                    detection=row,
                    log_file_path=matching_file,
                    delta_time=delta_time,
                    ts_cols=ts_cols,
                    detection_ts_col=detection_ts_col,
                    wt_id_col=wt_id_col,
                    signal_col=signal_col,
                    provider=provider,
                    model=model,
                    chunk_size=chunk_size)
                
                _write_jsonl(output_file_path,obj=output.model_dump(), mode="a")
                _write_jsonl(idx_path, obj={"idx": idx +1}, mode="w")
                last_idx = idx
                time.sleep(10)
                break
            except Exception as exc:
                attempts +=1
                warnings.warn(f"Error at detection idx={idx}\n"
                              f"attempt={attempts}, max retries={max_retries}\n"
                              f"Exc. Msg: {exc}")
                
                if attempts > max_retries:
                    warnings.warn(f"Deep search stopped at idx={idx}\n"
                                  f"Restart later to continue from this detection.\n")
                    return _all_results(output_file_path)
                
                time.sleep(wait_seconds)
                wait_seconds += wait_seconds*rnd.uniform(0.1, 2.5)
    
    #_write_jsonl(idx_path, obj={"idx": 0}, mode="w")
    return _all_results(output_file_path)