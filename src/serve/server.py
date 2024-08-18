import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse, FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

from src.serve.location_info_service import get_locations_info
from src.serve.aqi_predictor import AQIPredictor
from src.serve.metrics_service import get_production_metrics, get_model_metadata
from src.serve.mongo import ApiCallsClient
from src.util.constants import REPORTS_DIR

app = FastAPI()

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

predictor = AQIPredictor()
api_calls_client = ApiCallsClient()


@app.get("/", include_in_schema=False)
def read_root():
    return RedirectResponse(url="/docs")


@app.get("/api/locations")
def get_locations():
    return get_locations_info()


@app.get("/api/predict/{location_name}")
def predict_aqi(location_name: str):
    return predictor.predict(location_name)


@app.get("/api/reports/latest-predictions/{location_name}")
def get_predictions(location_name: str):
    return api_calls_client.get_api_calls_by_location(location_name)


@app.get("/api/reports/data-drift/{location_name}")
def get_data_drift(location_name: str):
    file_path = Path(f"reports/data-drift/{location_name}.html")

    if file_path.exists() and file_path.is_file():
        with file_path.open("r", encoding="utf-8") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    else:
        raise HTTPException(status_code=404, detail="File not found")


@app.get("/api/reports/data-stability/{location_name}")
def get_data_stability(location_name: str):
    file_path = Path(f"reports/data-stability/{location_name}.html")

    if file_path.exists() and file_path.is_file():
        with file_path.open("r", encoding="utf-8") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    else:
        raise HTTPException(status_code=404, detail="File not found")


@app.get("/api/reports/model-metrics/{location_name}")
def get_model_metrics(location_name: str):
    return get_production_metrics(location_name)


@app.get("/api/reports/model-metadata/{location_name}")
def get_metadata_for_model(location_name: str):
    return get_model_metadata(location_name)
