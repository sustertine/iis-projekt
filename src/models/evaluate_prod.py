import os

import pandas as pd
from dotenv import load_dotenv

from src.data.fetch_air_quality_data import fetch_air_quality_data
from src.serve.mongo import ApiCallsClient
from src.util.util import get_cities_and_coordinates

load_dotenv()
URL = os.getenv('AIR_QUALITY_URL')


def get_actual_data(lat, lon):
    air_quality_data = pd.DataFrame(fetch_air_quality_data(lat, lon)['hourly'])
    air_quality_data = air_quality_data[['time', 'european_aqi']]
    air_quality_data['time'] = pd.to_datetime(air_quality_data['time'])
    air_quality_data.set_index('time', inplace=True)
    air_quality_data.sort_index(inplace=True)
    return air_quality_data


def compare_predictions(location_name, lat, lon):
    client = ApiCallsClient()
    predictions = client.get_api_calls_by_location(location_name)
    for entry in predictions:
        id = entry.get('_id')
        location_name = entry.get('location_name')
        predictions = entry.get('predictions')

        evaluated_predictions = []
        actual = get_actual_data(lat, lon)
        for prediction in predictions:
            prediction_time = prediction.get('time')
            prediction_time = pd.to_datetime(prediction_time, dayfirst=True)

            nearest_idx = actual.index.get_indexer([prediction_time], method='nearest')[0]
            nearest_row = actual.iloc[nearest_idx]

            actual_aqi = nearest_row['european_aqi']

            mae = abs(actual_aqi - prediction.get('aqi'))
            mse = mae ** 2
            rmse = mse ** 0.5

            evaluated_predictions.append({
                'time': prediction_time,
                'actual_aqi': actual_aqi.astype(float),
                'aqi': prediction.get('aqi'),
                'mae': mae.astype(float),
                'mse': mse.astype(float),
                'rmse': rmse.astype(float)
            })

        client.add_actual(id, evaluated_predictions)


if __name__ == '__main__':
    cities = get_cities_and_coordinates()
    for city in cities:
        print(city)
        lat, lon = cities[city].get('lat'), cities[city].get('lon')
        compare_predictions(city, lat, lon)
