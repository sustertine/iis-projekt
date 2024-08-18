import concurrent.futures
import json
import logging
import os
from datetime import datetime, timedelta

import mlflow.pyfunc
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from fastapi import HTTPException
from mlflow import MlflowClient
from sklearn import set_config

from src.data.fetch_air_quality_data import fetch_air_quality_data
from src.data.fetch_weather_data import fetch_weather_data
from src.serve.mongo import ApiCallsClient

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(threadName)s/%(lineno)s] - %(levelname)s - %(message)s'
)

set_config(transform_output="pandas")

load_dotenv()
mlflow.set_tracking_uri(os.getenv('MLFLOW_TRACKING_URI'))
username = os.getenv('MLFLOW_TRACKING_USERNAME')
password = os.getenv('MLFLOW_TRACKING_PASSWORD')

mlflow_client = MlflowClient()
api_calls_client = ApiCallsClient()


def get_current_data(location_name: str):
    with open('resources/cities.json') as f:
        cities = json.load(f)
        lat = cities[location_name]['lat']
        lon = cities[location_name]['lon']

    weather_data = pd.DataFrame(fetch_weather_data(lat, lon)['hourly'])
    weather_data['time'] = pd.to_datetime(weather_data['time'])
    weather_data.set_index('time', inplace=True)
    weather_data.sort_index(inplace=True)

    air_quality_data = pd.DataFrame(fetch_air_quality_data(lat, lon)['hourly'])
    air_quality_data['time'] = pd.to_datetime(air_quality_data['time'])
    air_quality_data.set_index('time', inplace=True)
    air_quality_data.sort_index(inplace=True)

    common_times = weather_data.index.intersection(air_quality_data.index)

    common_times = common_times[-24:]

    weather_data = weather_data.loc[common_times]
    air_quality_data = air_quality_data.loc[common_times]

    joined_data = pd.merge(weather_data, air_quality_data, left_index=True, right_index=True)
    return joined_data


def load_model_components(city):
    logging.info(f"STARTED loading model components for: {city}")
    model_name = f"{city}_model"
    pipeline_name = f"{city}_pipeline"
    target_scaler_name = f"{city}_target_scaler"

    latest_model_version = mlflow_client.get_latest_versions(model_name)
    latest_pipeline_version = mlflow_client.get_latest_versions(pipeline_name)
    latest_target_scaler_version = mlflow_client.get_latest_versions(target_scaler_name)

    latest_model = mlflow_client.get_model_version(model_name, latest_model_version[-1].version)
    latest_pipeline = mlflow_client.get_model_version(pipeline_name, latest_pipeline_version[-1].version)
    latest_target_scaler = mlflow_client.get_model_version(target_scaler_name,
                                                           latest_target_scaler_version[-1].version)

    model_uri = f'runs:/{latest_model.run_id}/model'
    pipeline_uri = f'runs:/{latest_pipeline.run_id}/{pipeline_name}'
    target_scaler_uri = f'runs:/{latest_target_scaler.run_id}/{target_scaler_name}'

    model = mlflow.pyfunc.load_model(model_uri)
    pipeline = mlflow.sklearn.load_model(pipeline_uri)
    target_scaler = mlflow.sklearn.load_model(target_scaler_uri)

    logging.info(f"COMPLETED loading model components for: {city}")

    return (model_name, model), (pipeline_name, pipeline), (target_scaler_name, target_scaler)


class AQIPredictor:
    def __init__(self):
        self.model_map = {}

        with open('resources/cities.json') as f:
            cities = dict(json.load(f))

        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            start_time = datetime.now()

            future_to_city = {executor.submit(load_model_components, city): city for city in cities}
            for future in concurrent.futures.as_completed(future_to_city):
                city = future_to_city[future]
                try:
                    model_tuple, pipeline_tuple, target_scaler_tuple = future.result()
                    self.model_map[model_tuple[0]] = model_tuple[1]
                    self.model_map[pipeline_tuple[0]] = pipeline_tuple[1]
                    self.model_map[target_scaler_tuple[0]] = target_scaler_tuple[1]
                except Exception as exc:
                    print(f'{city} generated an exception: {exc}')

        logging.info(f"COMPLETED loading all model components in: {datetime.now() - start_time}s")

    def predict(self, location_name: str):
        if f'{location_name}_model' not in self.model_map:
            raise HTTPException(status_code=404, detail=f"Model for location {location_name} not found")
        current_date_time = datetime.now()
        data = get_current_data(location_name)

        data_dict = data.to_dict(orient='records')[0]
        data_dict['location_name'] = location_name
        data_dict['time'] = current_date_time.isoformat()

        current_aqi = self.model_map[f'{location_name}_target_scaler'].transform(
            data['european_aqi'].values.reshape(-1, 1))
        data = self.model_map[f'{location_name}_pipeline'].transform(data)
        data['european_aqi'] = current_aqi
        data.dropna(inplace=True)

        data = np.expand_dims(data.values, axis=0)
        prediction = self.model_map[f'{location_name}_model'].predict(data)
        prediction = self.model_map[f'{location_name}_target_scaler'].inverse_transform(prediction)

        prediction = prediction.flatten().tolist()
        predictions_list = []
        for i in range(len(prediction)):
            future_time = current_date_time + timedelta(hours=i + 1)
            predictions_list.append({
                'time': future_time.strftime('%d-%m-%Y %H:%M:%S'),
                'aqi': prediction[i]
            })

        data_dict['predictions'] = predictions_list
        api_calls_client.create_api_call(data_dict)

        return predictions_list
