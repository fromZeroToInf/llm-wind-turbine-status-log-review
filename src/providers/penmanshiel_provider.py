from __future__ import annotations
from typing import Any
import pandas as pd
import constants as cts

class penmanshielProvider:
    
    def get_detection_ts(self, detection: pd.Series)-> pd.Timestamp:
        return pd.to_datetime(detection[cts.DET_TS_COL])
    
    def get_wt_id(self, detection: pd.Series)-> pd.Timestamp:
        return detection[cts.WT_ID]
    
    def get_signal_name(self, detection: pd.Series) -> str:
        return str(detection[cts.SIGNAL])
    
    def get_signal_window(self, scada_df: pd.DataFrame, detection: pd.Series, prepost_window: int, time_unit: str) -> pd.DataFrame:
        detection_ts = self.get_detection_ts(detection)
        wt_id = self.get_wt_id(detection)
        signal_name = self.get_signal_name(detection)
        start_ts = detection_ts - pd.Timedelta(unit=time_unit)
        end_ts = detection_ts + pd.Timedelta(unit=time_unit)
        
        window = scada_df.loc[
            (scada_df[cts.WT_ID] == wt_id)
            & (pd.to_datetime(scada_df[cts.DET_TS_COL]))
        ]
    
    def get_detection_metrics(self, detection: pd.Series) -> dict[str, Any]:
        ...