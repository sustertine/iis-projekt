import os

import mlflow
from dotenv import load_dotenv
from fastapi import HTTPException
from mlflow import MlflowClient

load_dotenv()
mlflow.set_tracking_uri(os.getenv('MLFLOW_TRACKING_URI'))
username = os.getenv('MLFLOW_TRACKING_USERNAME')
password = os.getenv('MLFLOW_TRACKING_PASSWORD')

mlflow_client = MlflowClient()


def get_production_metrics(location_name: str):
    model_name = f"{location_name}_model"

    try:
        latest_model_versions = mlflow_client.get_latest_versions(model_name)
        if not latest_model_versions:
            raise HTTPException(status_code=404, detail=f"No versions found for model: {model_name}")

        latest_version = latest_model_versions[-1]
        run_id = latest_version.run_id

        run = mlflow_client.get_run(run_id)

        metrics = run.data.metrics
        return metrics

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def get_model_metadata(location_name: str):
    model_name = f"{location_name}_model"

    try:
        latest_model_versions = mlflow_client.get_latest_versions(model_name)
        if not latest_model_versions:
            raise HTTPException(status_code=404, detail=f"No versions found for model: {model_name}")

        latest_version = latest_model_versions[-1]
        run_id = latest_version.run_id
        version = latest_version.version

        model_info = mlflow_client.get_run(run_id).info
        model_details = {
            "model_name": model_name,
            "version": version,
            "run_id": run_id,
            "start_time": model_info.start_time,
            "end_time": model_info.end_time,
            "status": model_info.status,
            "params": mlflow_client.get_run(run_id).data.params,
        }

        return model_details

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
