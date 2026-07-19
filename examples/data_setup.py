# import sys
# from pathlib import Path
# sys.path.insert(0, str(Path.cwd().parent))
import requests
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
from glob import glob
from zipfile import ZipFile
import os
from joblib import Parallel, delayed
import warnings
from src import constants as cts
import pandas as pd
from pathlib import Path

URLS = [
    "https://zenodo.org/records/8253010/files/Penmanshiel_SCADA_2016_WT01-10_3107.zip?download=1",
    "https://zenodo.org/records/8253010/files/Penmanshiel_SCADA_2016_WT11-15_3107.zip?download=1",
    "https://zenodo.org/records/8253010/files/Penmanshiel_SCADA_2017_WT01-10_3114.zip?download=1",
    "https://zenodo.org/records/8253010/files/Penmanshiel_SCADA_2017_WT11-15_3115.zip?download=1",
    "https://zenodo.org/records/8253010/files/Penmanshiel_SCADA_2018_WT01-10_3113.zip?download=1",
    "https://zenodo.org/records/8253010/files/Penmanshiel_SCADA_2018_WT11-15_3116.zip?download=1",
    "https://zenodo.org/records/8253010/files/Penmanshiel_SCADA_2019_WT01-10_3112.zip?download=1",
    "https://zenodo.org/records/8253010/files/Penmanshiel_SCADA_2019_WT11-15_3117.zip?download=1",
    "https://zenodo.org/records/8253010/files/Penmanshiel_SCADA_2020_WT01-10_3109.zip?download=1",
    "https://zenodo.org/records/8253010/files/Penmanshiel_SCADA_2020_WT11-15_3118.zip?download=1",
    "https://zenodo.org/records/8253010/files/Penmanshiel_SCADA_2021_WT01-10_4460.zip?download=1",
    "https://zenodo.org/records/8253010/files/Penmanshiel_SCADA_2021_WT11-15_4461.zip?download=1",
    "https://zenodo.org/records/8253010/files/Penmanshiel_SCADA_2022_WT01-10_4462.zip?download=1",
    "https://zenodo.org/records/8253010/files/Penmanshiel_SCADA_2022_WT11-15_4463.zip?download=1",
]

def download_file(url):
    def filename_from_url(url) -> str:
        fn = url.split("/")[-1].split("?")[0]
        return fn
    
    response = requests.get(url, stream=True)
    fn = filename_from_url(url)
    print(f"Downloading: {fn}...")
    with open(cts.PATH_SIGNALS/fn, mode="wb") as file:
        for chunk in response.iter_content(chunk_size=100*1024):
            file.write(chunk)
    print(f"Download: {fn} [finished]")
    
def download_penmanshiel(urls: list[str]):
    Path(cts.PATH_SIGNALS).mkdir(parents=True, exist_ok=True)
    downloaded_files = list(cts.PATH_SIGNALS.glob("*.zip"))
    downloaded_files = ["https://zenodo.org/records/8253010/files/"+str(file.name) +"?download=1" for file in downloaded_files]
    urls = list(set(urls).difference(set(downloaded_files)))
    print(f"len(urls):{len(URLS)}, diff urls={len(urls)}")
    if len(urls) > 0:
        with ThreadPoolExecutor(max_workers=8) as ex:
            ex.map(lambda url: download_file(url), urls)

def extract_all_zips(path: Path):
    def _extract_zip(file:Path) -> None:
        with ZipFile(file, mode="r") as zip_file:
            items = zip_file.namelist()
            items = [item for item in items if item.startswith("Turbine")]
            zip_file.extractall(file.parent, members=items)
            
    zip_files = list(path.glob("*.zip"))
    if zip_files:
        list(tqdm(
            map(_extract_zip, zip_files),
            total=len(zip_files),
            desc="Unpacking ZIP files",
            unit="File",
        ))


COLUMNS_TO_SELECT = [
    'Ambient temperature (converter) (°C)',
    'Date and time',
    'Drive train acceleration (mm/ss)',
    'Gear oil inlet pressure (bar)',
    'Gear oil pump pressure (bar)',
    'Gearbox speed (RPM)',
    'Generator bearing front temperature (°C)',
    'Generator bearing rear temperature (°C)',
    'Generator RPM (RPM)',
    'Hub temperature (°C)',
    'Motor current axis 1 (A)',
    'Motor current axis 2 (A)',
    'Motor current axis 3 (A)',
    'Nacelle ambient temperature (°C)',
    'Nacelle position (°)',
    'Nacelle temperature (°C)',
    'Power (kW)',
    'Rotor bearing temp (°C)',
    'Rotor speed (RPM)',
    'Stator temperature 1 (°C)',
    'Temp. top box (°C)',
    'Temperature motor axis 1 (°C)',
    'Temperature motor axis 2 (°C)',
    'Temperature motor axis 3 (°C)',
    'Vane position 1+2 (°)',
    'Wind direction (°)',
    'Wind speed (m/s)',
    "Blade angle (pitch position) A (°)",
    "Blade angle (pitch position) B (°)",
    "Blade angle (pitch position) C (°)",
    "Front bearing temperature (°C)",
    "Gear oil inlet temperature (°C)",
    "Gear oil temperature (°C)",
    "Rear bearing temperature (°C)",
    "Tower Acceleration X (mm/ss)",
    "Tower Acceleration y (mm/ss)",
    "Transformer cell temperature (°C)",
    "Transformer temperature (°C)",
    "Yaw bearing angle (°)",
]

def cleanup_zip_files():
    zips = list(cts.PATH_SIGNALS.glob("*.zip"))
    [os.remove(file) for file in tqdm(zips, desc="Cleaning up ZIP files")]

def preprocessing_merge_files(path:Path):
    wts = [1,2,4,5,6,7,8,9,10,11,12,13,14,15]
    def _clean_csv(fn:Path)-> pd.DataFrame:
        df = pd.read_csv(fn, skiprows=9)
        df.columns = [col.lstrip("#").strip() for col in df.columns]
        df = df.loc[:, COLUMNS_TO_SELECT]
        return df
    
    def _process_wt(wt:int):
        files = list(cts.PATH_SIGNALS.glob(f"Turbine_Data*_0{wt}_*" if wt < 10 else f"Turbine_Data*_{wt}_*" ))
        dfs = list(map(_clean_csv, files))
        df = pd.concat(dfs, axis=0)
        df[cts.WT_ID] = wt
        df = df.loc[:, [cts.WT_ID] + COLUMNS_TO_SELECT]
        df.rename(columns={"Tower Acceleration y (mm/ss)": "Tower Acceleration Y (mm/ss)"}, inplace=True)
        df[cts.DET_TS_COL] = pd.to_datetime(df[cts.DET_TS_COL], errors="coerce")
        df.sort_values(by=[cts.DET_TS_COL], ascending=True)
        df = df[(df[cts.DET_TS_COL] >= pd.to_datetime("2020-05-01 04:10:00")) & (df[cts.DET_TS_COL] <= pd.to_datetime("2022-12-31 23:50:00"))]
        df.to_csv(cts.PATH_SIGNALS/f"WT_{wt}.csv", index=False)
        [os.remove(file) for file in files]
        
    with warnings.catch_warnings():
        warnings.simplefilter(action="ignore", category=pd.errors.PerformanceWarning)
        Parallel(n_jobs=8, backend="threading")(
            delayed(_process_wt)(wt) for wt in  tqdm(wts, desc="Process Files", unit="File")
        )

def penmanshiel_setup():
    
    download_penmanshiel(URLS)
    extract_all_zips(cts.PATH_SIGNALS)
    preprocessing_merge_files(cts.PATH_SIGNALS)
    cleanup_zip_files()

penmanshiel_setup()
