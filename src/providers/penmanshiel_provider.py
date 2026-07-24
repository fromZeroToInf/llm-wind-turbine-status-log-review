from __future__ import annotations
from typing import Any
import pandas as pd
import src.constants as cts
from joblib import Parallel, delayed

class penmanshielProvider:
    
    @staticmethod
    def _find_row(dets_df:pd.DataFrame, res:dict)-> pd.DataFrame | pd.Series:
        row = dets_df[
                (dets_df[cts.WT_ID].astype(str) == str(res["wt_id"]))
                 & (pd.to_datetime(dets_df[cts.DET_TS_COL]) == pd.to_datetime(res["detection_ts"]))
                 & (dets_df[cts.SIGNAL] == res["relevant_signal"])
                 ]
        if len(row) == 0:
            raise ValueError(f"Result:{res}\n not in dets_df")
        return row
    
    @classmethod
    def _merge_dets_with_results(cls,dets_df: pd.DataFrame, results: list[dict]) -> pd.DataFrame:
        rows = [
        cls._find_row(dets_df, result)
        for result in results
        ]
        if len(rows) <= 1:
            if len(rows) == 1 and isinstance(rows[0], pd.DataFrame):
                return rows[0]
            elif isinstance(rows[0], pd.Series):
                return pd.DataFrame(rows[0]).transpose()
            elif len(rows) ==0:
                raise ValueError("No rows found.")
            
        return pd.concat(rows, ignore_index=True)
        

    @classmethod
    def _load_detections(cls, mime_type:str = "csv") -> pd.DataFrame:
        file = list(cts.PATH_DETECTIONS.glob(f"*.{mime_type}"))[0]
        detections_df = pd.read_csv(file)
        detections_df = detections_df[detections_df["z_shift"] > 0].sort_values(by="z_shift", ascending=False)
        detections_df = detections_df.reset_index()
        detections_df[cts.DET_TS_COL] = pd.to_datetime(detections_df[cts.DET_TS_COL])
        detections_df[cts.WT_ID] = detections_df[cts.WT_ID].astype(str)
        return detections_df
    
    @classmethod
    def get_all_detections(cls, results: list[dict]) -> list[dict[str,Any]]:
        
        dets_df = cls._load_detections()
        
        dets_df = cls._merge_dets_with_results(dets_df,results)

        dets_df = dets_df.round(2)
        dets_df = dets_df.fillna("NAN")
        dets_df = dets_df[[ 'WT_ID', 're_at_ts', 'Date and time', 'signal_name', 'window_start', 'window_end', 'wind_center', 'value_at_ts','z_shift']]
        cols = list(dets_df.columns)
        
        def to_dict(idx,row) -> dict[str,Any]:
            a_dict = {}
            a_dict["detection_id"] = idx
            for col in cols:
                a_dict[col] = row[col]
            
            return a_dict
        
        dets = [to_dict(idx,row) for idx, row in dets_df.iterrows()]

        return dets

    @classmethod
    def get_detection(cls, wt_id:str, ts:str, signal:str)-> pd.DataFrame:
        df = cls._load_detections()

        # df[cts.WT_ID] = df[cts.WT_ID].astype(str)
        # df[cts.DET_TS_COL] = pd.to_datetime(
        #     df[cts.DET_TS_COL],
        #     errors="coerce",
        # )

        detection = df[
            (df[cts.WT_ID] == str(wt_id))
            & (df[cts.DET_TS_COL] == pd.to_datetime(ts))
            & (df[cts.SIGNAL] == signal)
        ]

        if detection.empty:
            raise ValueError(
                f"No detection found for WT_ID={wt_id!r}, timestamp={ts!r}"
            )

        if len(detection) > 1:
            raise ValueError(
                f"Expected one detection, found {len(detection)} "
                f"for WT_ID={wt_id!r}, timestamp={ts!r}"
            )

        return detection
    
    def get_scada(self, wt_id:str)->pd.DataFrame:
        file= list(cts.PATH_SIGNALS.glob(f"WT_{wt_id}.csv"))[0]
        return pd.read_csv(file)
    
    def get_detection_ts(self, detection: pd.DataFrame)-> pd.Timestamp:
        return pd.to_datetime(detection.iloc[0][cts.DET_TS_COL])
    
    def get_wt_id(self, detection: pd.DataFrame)-> str:
        return str(detection.iloc[0][cts.WT_ID])
    
    def get_signal_name(self, detection: pd.DataFrame) -> str:
        return str(detection.iloc[0][cts.SIGNAL])
    
    def get_signal_window(self, scada_df: pd.DataFrame, detection: pd.DataFrame) -> list[list[str, float]]:
        detection_ts = self.get_detection_ts(detection)
        wt_id = self.get_wt_id(detection)
        signal_name = self.get_signal_name(detection)
        start_ts = pd.to_datetime(detection_ts - cts.PRE_POST_WINDOW)
        end_ts = pd.to_datetime(detection_ts + cts.PRE_POST_WINDOW)
        
        window = scada_df.loc[
            (scada_df[cts.WT_ID].astype(str) == wt_id)
            & (pd.to_datetime(scada_df[cts.DET_TS_COL]) >= start_ts)
            & (pd.to_datetime(scada_df[cts.DET_TS_COL]) <= end_ts),
            [cts.DET_TS_COL, signal_name]
        ].copy()
        
        window[cts.DET_TS_COL] = window[cts.DET_TS_COL].astype(str)
        window[signal_name] = window[signal_name].astype("float")
        window = window.round({signal_name:1})
        data_list= []
        for _, row in window.iterrows():
            value = row[signal_name]
            data_list.append([row[cts.DET_TS_COL], 
                              None if pd.isna(value) else float(value)])
        
        return data_list
    
    def get_detection_metrics(self, detection: pd.DataFrame) -> dict[str, Any]:
        cols=[
            "z_at_ts",
            "z_shift",
            "delta_mean",
            "values_at_ts",
            "mean_baseline",
            "std_baseline",
        ]
    
        return {
            col: detection.get(col)
            for col in cols
            if col in detection.index
        }
    
    def get_powercurve(self) -> list:
        df_pc = pd.read_csv(cts.PATH_POWERCURVE/"pc_interpol.csv").rename(columns={"Unnamed: 0": "Wind Speed (m/s)"})
        list_pc = list(df_pc.values.reshape(-1,2).tolist())
        return list_pc
    
    def get_data_for_pc(self, wt_id: str, window_half_size: int, det_ts: str) -> tuple[list, list]:
        file = list(cts.PATH_SIGNALS.glob(f"WT_{wt_id}.csv"))[0]
        wt_df = pd.read_csv(file)
        wt_df = wt_df[["Wind speed (m/s)", "Power (kW)", cts.DET_TS_COL, cts.WT_ID]]
        det_ts = pd.to_datetime(det_ts)
        delta = pd.Timedelta(hours=window_half_size)
        wt_df[cts.DET_TS_COL] = pd.to_datetime(wt_df[cts.DET_TS_COL])
        det_pair = list(wt_df[wt_df[cts.DET_TS_COL] == det_ts][["Wind speed (m/s)", "Power (kW)"]].values.reshape(-1,2).tolist())
        mask = wt_df[cts.DET_TS_COL].between(det_ts -delta , det_ts+delta)
        wt_df = wt_df[mask].round(2)
        wt_df = wt_df[["Wind speed (m/s)", "Power (kW)"]]
        points = list(wt_df.values.reshape(-1,2).tolist())
        return points,det_pair