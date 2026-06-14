from typing import Optional
import os
from pathlib import Path
import pandas as pd

def load_logfile(filePath:Path, 
                 detection_ts: pd.Timestamp, 
                 delta_time: pd.Timedelta, 
                 ts_cols: list[str],
                 wt_id: Optional[str], 
                 wt_col: Optional[str]) -> pd.DataFrame:
    
    if not os.path.exists(filePath):
        raise ValueError("Path does not exist.")
    
    df = pd.read_csv(filePath, dtype={"Comment": "string"}, low_memory=False)
    if len(ts_cols) ==2:
        df[ts_cols[0]] = pd.to_datetime(df[ts_cols[0]], errors="coerce")
        df[ts_cols[1]] = pd.to_datetime(df[ts_cols[1]], errors="coerce")
    else:
        raise ValueError("Please Check ts_cols, it must contain to two columns (start and end)")
    
    if wt_id and wt_col:
        if wt_col not in list(df.columns):
            raise ValueError(f"The column: {wt_col} does not exist in the table")
        if not wt_id == str(df[wt_col].unique()[0]):
            raise ValueError("WT ID does not exist")
    end = detection_ts + delta_time
    start = detection_ts - delta_time
    df = df[(df["Timestamp start"] >= start) & (df["Timestamp end"] <= end)]
    
    return df