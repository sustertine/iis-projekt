import os

import pandas as pd

from src.util.constants import DATA_RAW_DIR, DATA_PROCESSED_DIR


def remove_duplicates():
    for file in os.listdir(f'{DATA_RAW_DIR}/weather'):
        file_path = f'{DATA_RAW_DIR}/weather/{file}'
        df = pd.read_csv(file_path)
        df.drop_duplicates(inplace=True)
        df.to_csv(file_path, index=False)

    for file in os.listdir(f'{DATA_RAW_DIR}/air-quality'):
        file_path = f'{DATA_RAW_DIR}/air-quality/{file}'
        df = pd.read_csv(file_path)
        df.drop_duplicates(inplace=True)
        df.to_csv(file_path, index=False)


def join_weather_data():
    for file in os.listdir(f'{DATA_RAW_DIR}/weather'):
        city = file.split('.')[0]
        weather_df = pd.read_csv(f'{DATA_RAW_DIR}/weather/{file}')
        air_quality_df = pd.read_csv(f'{DATA_RAW_DIR}/air-quality/{file}')

        weather_df.drop_duplicates(subset='time', inplace=True)
        air_quality_df.drop_duplicates(subset='time', inplace=True)

        weather_df['time'] = pd.to_datetime(weather_df['time'])
        air_quality_df['time'] = pd.to_datetime(air_quality_df['time'])

        df = pd.merge(weather_df, air_quality_df, on='time', how='inner')
        df.to_csv(f'{DATA_PROCESSED_DIR}/{city}.csv', index=False)


def main():
    remove_duplicates()
    join_weather_data()


if __name__ == '__main__':
    main()
