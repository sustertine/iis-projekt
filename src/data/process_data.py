import os

import pandas as pd

from src.util.constants import DATA_RAW_DIR, DATA_PROCESSED_DIR, DATA_REFERENCE_DIR


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


def create_reference_copies():
    for file in os.listdir(DATA_PROCESSED_DIR):
        file_path = f'{DATA_PROCESSED_DIR}/{file}'
        df = pd.read_csv(file_path)
        reference_file_path = f'{DATA_REFERENCE_DIR}/{file}'

        if os.path.exists(reference_file_path):
            os.remove(reference_file_path)

        df.to_csv(reference_file_path, index=False)


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


def resample_data():
    for file in os.listdir(DATA_PROCESSED_DIR):
        df = pd.read_csv(f'{DATA_PROCESSED_DIR}/{file}', index_col='time')
        df = df.resample('H').mean()
        df.fillna(method='ffill', inplace=True)
        df.to_csv(f'{DATA_PROCESSED_DIR}/{file}', index=True)


def main():
    remove_duplicates()
    create_reference_copies()
    join_weather_data()
    resample_data()


if __name__ == '__main__':
    main()
