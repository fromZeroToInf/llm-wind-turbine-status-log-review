from pathlib import Path
from .getprojectroot import define_project_root_path

PATH_PROJECT_ROOT =define_project_root_path()
PATH_STATUS_LOGS = PATH_PROJECT_ROOT/"examples/status_logs/"
PATH_DETECTIONS = PATH_PROJECT_ROOT/"examples/detections/"

"""
Set the columns of the status logs    
"""
LOG_COLS = [
    "Timestamp start",
    "Timestamp end",
    "WT_ID",
    "Status",
    "Code",
    "Message",
    "Comment",
]