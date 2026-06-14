from pathlib import Path
import pytest
import pandas as pd
import sys
from src import helper, constants

def test_load_logfile_returns_empty_list() -> None:
    chunks = helper.load_logfile(list(Path(constants.PATH_STATUS_LOGS).glob("*.csv"))[0],
                                 wt_col=None,
                                 wt_id=None,
                                 detection_ts=pd.to_datetime("2020-11-22 20:00:00"),
                                 ts_cols=["Timestamp start", "Timestamp end"], 
                                 delta_time=pd.Timedelta(days=1)
                                 )
    
    assert len(chunks) == 1, "chunks is empty"
    assert chunks[0].empty == True, "df is not empty"
    
def test_load_logfile_returns_chunks() -> None:
    
    chunks = helper.load_logfile(list(Path(constants.PATH_STATUS_LOGS).glob("*.csv"))[0],
                                 wt_col=None,
                                 wt_id=None,
                                 detection_ts=pd.to_datetime("2020-11-22 20:00:00"),
                                 ts_cols=["Timestamp start", "Timestamp end"], 
                                 delta_time=pd.Timedelta(days=30)
                                 )
    
    assert len(chunks) == 14, "chunks length is not 14 empty"
    