from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import src.signal_context as sc
import src.providers.penmanshiel_provider as pp
from src.llm_results import llm_results
import src.constants as cts

llm_res = llm_results(cts.PATH_OUTPUT/cts.FN_OUTPUT)


app = FastAPI()

app.mount("/static", StaticFiles(directory="frontend"), name="static")


@app.get("/")
def dashboard():
    return FileResponse("frontend/index.html")

@app.get("/review/{detection_id}")
def review_detection(detection_id: str):
    return FileResponse("frontend/review.html")

@app.get("/api/detections")
def get_detection():
    return pp.penmanshielProvider().get_all_detections(llm_res.entries)


@app.get("/api/reviews/{detection_id}")
def get_review(detection_id: int):
    return llm_res.get_result(detection_id)
    

@app.get("/api/reviews/{wt_id}/{timestamp}/{signal}")
def get_signal(wt_id: str, timestamp: str, signal: str):
     scontext = sc.compute_signal_context(wt_id,timestamp,signal,pp.penmanshielProvider())
     return scontext

@app.get("/api/reviews/{wt_id}/{timestamp}/{half_window_size}/powercurve")
def get_powercurve(wt_id:str, timestamp:str, half_window_size:int):
    pc = sc.data_for_powercurve(wt_id, half_window_size, timestamp, pp.penmanshielProvider())
    return pc

@app.get("/api/test-signal")
def get_test_signal():
    return {
        "points": [
            ["2020-01-01T00:00:00", 1.0],
            ["2020-01-01T00:10:00", 10.4],
            ["2020-01-01T00:20:00", 100.2]
        ]
    }