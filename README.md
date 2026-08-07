# AI assisted status log reviewer

LLM assisted status log reviewer to find relevant information for anomaly detections and to prioritize relevant detections.

Dieses Projekt ist ein Follow-up meines Projekts „Explorative AD in Windturbinen-SCADA-Daten unter Verwendung eines AE“ (https://github.com/fromZeroToInf/Explorative-AD-in-Wind-Turbine-SCADA-Data-Using-an-AE). This projected is intended to be a feasibility test and has a explorative character.

This project aims to filter undocumented detection events.

# Installation via PDM

```Python
pdm install
```

# Non-mandatory Requirements

You need a GEMINI API KEY to run the workflow from the notebook. Store your KEY in .env.
It is also possible to run a OLLAMA model locally, which is not recommended due to the quality of the model results.

# Demo

Run the notebook data_test_ipynb from the directory examples.
For visualization of the processed data from the LLM run in terminal

```Bash
uvicorn src.api.main:app --reload
# under windows
uvicorn.exe src.api.main:app --reload
```

and have a look at your browser under the stated URL from the terminal.
