from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

from src.serve.location_info_service import get_locations_info
from src.serve.aqi_predictor import AQIPredictor

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

@app.get("/", include_in_schema=False)
def read_root():
    return RedirectResponse(url="/docs")


@app.get("/api/locations")
def get_locations():
    return get_locations_info()


@app.get("/api/predict-aqi/{location_name}")
def predict_aqi(location_name: str):
    return predictor.predict(location_name)
