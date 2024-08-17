import os
from datetime import datetime, timedelta
from random import random

import mlflow.pyfunc
import numpy as np
from fastapi import HTTPException
from dotenv import load_dotenv
from mlflow import MlflowClient
from sklearn import set_config

set_config(transform_output="pandas")

load_dotenv()
mlflow.set_tracking_uri(os.getenv('MLFLOW_TRACKING_URI'))
username = os.getenv('MLFLOW_TRACKING_USERNAME')
password = os.getenv('MLFLOW_TRACKING_PASSWORD')

client = MlflowClient()


class AQIPredictor:

    def __init__(self):
        self.model_map = {}

        loaded_models = client.search_registered_models()

        for rm in loaded_models:
            model_uri = client.get_model_version_download_uri(rm.name, rm.latest_versions[0].version)
            model_info = mlflow.models.Model.load(model_uri)
            model_flavors = model_info.flavors.keys()

            if 'python_function' in model_flavors:
                self.model_map[rm.name] = mlflow.pyfunc.load_model(model_uri=f'models:/{rm.name}/latest')
            elif 'sklearn' in model_flavors:
                self.model_map[rm.name] = mlflow.sklearn.load_model(model_uri=f'models:/{rm.name}/latest')

    def predict(self, location_name: str):
        current_date_time = datetime.now()
        return [
            {
                "time": (current_date_time + timedelta(hours=i)).strftime("%Y-%m-%d %H:%M:%S"),
                "aqi": random() * 100
            }
            for i in range(24)
        ]
