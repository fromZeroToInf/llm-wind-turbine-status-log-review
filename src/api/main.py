from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

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
    return [
        {
            "detection_id": "1",
            "wt_id": "1",
            "signal_name": "test signal",
            "detection_ts": "2020-11-22T20:20:00",
        },
        {
            "detection_id": "2",
            "wt_id": "1",
            "signal_name": "test signal",
            "detection_ts": "2020-12-22T20:20:00",
        }
    ]

@app.get("/api/reviews/{detection_id}")
def get_review(detection_id: str):
    return {
            "wt_id": "1",	
            "detection_id": "1",	
            "detection_ts": "2020-11-22T20:20:00",	
            "relevant_signal": "test signal",	
            "anomaly_description_reasoning": "test",	
            "relevant_logs": [{"log_index": "64234", "log_start_ts": "2021-01-18 11:04:27", "log_end_ts": "2021-01-18 17:06:53", "reasoning": "This log indicates an overload condition for generator fan 1. Generator fans are critical for cooling the generator, and an overload suggests a malfunction or reduced efficiency in the cooling system. This directly impacts the generator's thermal management and can lead to increased bearing temperatures. The log occurred three days before the detection, making it temporally relevant to the developing temperature anomaly."}, {"log_index": "64235", "log_start_ts": "2021-01-18 11:04:27", "log_end_ts": "2021-01-18 17:06:53", "reasoning": "Similar to log 64234, this log indicates an overload condition for generator fan 2. A problem with any of the generator cooling fans can lead to insufficient heat dissipation, directly contributing to elevated generator bearing temperatures. This log is temporally relevant, occurring shortly before the detected temperature increase."}, {"log_index": "64236", "log_start_ts": "2021-01-18 11:04:27", "log_end_ts": "2021-01-18 17:06:52", "reasoning": "This log indicates an overload condition for generator fan 3. The simultaneous overload warnings for multiple generator fans (1, 2, and 3) strongly suggest a systemic issue with the generator's cooling system. This directly correlates with the observed increase in generator bearing front temperature, providing concrete evidence for a potential cause of overheating. The timing is also relevant, preceding the anomaly detection."}, {"log_index": "64243", "log_start_ts": "2021-01-18 11:58:17", "log_end_ts": "2021-01-18 17:01:45", "reasoning": "The 'Timeout brake closed' warning indicates a potential issue with the braking system. The brake is typically located on the high-speed shaft, physically close to the generator. A malfunction in the brake could lead to abnormal mechanical stress, friction, or heat generation that could transfer to and affect the generator bearings, contributing to increased temperature. This event occurred approximately three days before the detection."}, {"log_index": "64309", "log_start_ts": "2021-01-19 15:15:42", "log_end_ts": "2021-01-19 16:02:25", "reasoning": "A 'High rotor speed nacelle' stop indicates that the turbine experienced excessive rotor speeds. High rotor speed directly translates to high generator speed. Such events can impose significant mechanical and thermal stress on the generator bearings due to increased rotational friction and load, potentially leading to an increase in their operating temperature. This event occurred two days before the detection of elevated generator bearing temperature."}],	
            "overall_assessment": "possibly_undocumented_anomaly",	
            "overall_reasoning": "test",	
            "n_relevant_logs": "1",
        }
    

@app.get("/api/reviews/{detection_id}/signal")
def get_signal(detection_id: str):
     return {
        "detection_id": detection_id,
        "detection_ts": "2020-11-22 20:20:00",
        "points": 
            [
                ["2020-11-22T19:40:00", 31.2],
                ["2020-11-22T19:50:00", 32.0],
                ["2020-11-22T20:00:00", 36.5],
                ["2020-11-22T20:10:00", 35.1]
            ]
    }




@app.get("/api/test-signal")
def get_test_signal():
    return {
        "points": [
            ["2020-01-01T00:00:00", 1.0],
            ["2020-01-01T00:10:00", 10.4],
            ["2020-01-01T00:20:00", 100.2]
        ]
    }