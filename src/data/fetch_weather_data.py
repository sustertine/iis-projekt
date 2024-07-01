import os

import pandas as pd
import requests

from src.util.constants import WEATHER_URL, DATA_RAW_DIR
from src.util.util import get_cities_and_coordinates


def fetch_weather_data(lat, lon):
    base_url, parameters = WEATHER_URL.split('?')
    modified_url = f"{base_url}?latitude={lat}&longitude={lon}&{parameters}"
    response = requests.get(modified_url)
    return response.json()


def save_write_to_csv(data, city):
    file_path = f'{DATA_RAW_DIR}/weather/{city}.csv'
    df = pd.DataFrame(data['hourly'])
    df.set_index('time', inplace=True)
    df.drop_duplicates(inplace=True)

    if os.path.exists(file_path):
        df.to_csv(file_path, mode='a', header=False)
    else:
        df.to_csv(file_path)


def main():
    coordinates = get_cities_and_coordinates()
    for item in coordinates.items():
        city, lat_lon = item
        lat = lat_lon['lat']
        lon = lat_lon['lon']
        data = fetch_weather_data(lat, lon)
        save_write_to_csv(data, city)


if __name__ == '__main__':
    main()
