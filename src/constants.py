from pathlib import Path
from .getprojectroot import define_project_root_path

PATH_PROJECT_ROOT =define_project_root_path()
PATH_STATUS_LOGS = PATH_PROJECT_ROOT/"examples/status_logs/"
PATH_DETECTIONS = PATH_PROJECT_ROOT/"examples/detections/"

"""
Set the columns of the status logs    
"""
TS_START = "Timestamp start"
TS_END = "Timestamp end"

LOG_COLS = [
    TS_START,
    TS_END,
    "WT_ID",
    "Status",
    "Code",
    "Message",
    "Comment",
]
TS_COLS = [TS_START, TS_END]

"""
Detection Columns
"""
DET_TS_COL = "Date and time"
WT_ID = "WT_ID"
SIGNAL = "signal_name"

"""
Columns to round to 2 decimal numbers
"""
COLS_TO_ROUND = ["re_at_ts",
            "value_at_ts",
            "delta_at_ts",
            "z_at_ts",
            "mean_baseline",
            "std_baseline",
            "mean_event",
            "std_event",
            "delta_mean",
            "z_shift",]

"""
Control tokens
"""
MAX_TOKENS= 2048
