import tensorflow as tf

import json

from keras import Sequential
from keras.layers import LSTM, Dense

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler

from src.models.feature_engineer import FeatureEngineer
from src.util.constants import RESOURCES_DIR, DATA_PROCESSED_DIR


def create_model(n_time_steps, n_features):
    print(n_time_steps, n_features)
    model = Sequential()
    model.add(LSTM(50, input_shape=(n_time_steps, n_features)))  # train_X.shape[1], train_X.shape[2
    model.add(Dense(24))
    model.compile(loss='mse', optimizer='adam')
    return model


def get_cities():
    for city in json.load(open(f"{RESOURCES_DIR}/cities.json")):
        yield city


def read_csv(path):
    return pd.read_csv(path, index_col=0, parse_dates=True)


def preprocess_data(df):
    minmax_scaler = MinMaxScaler()
    target_scaler = MinMaxScaler()

    target_columns = ['european_aqi']
    feature_columns = ['ozone', 'air_quality_combined', 'nitrogen_dioxide', 'pollutant_range', 'temperature_2m',
                       'relative_humidity_2m', 'apparent_temperature', 'humidity_adjusted_temp', 'carbon_monoxide']

    column_transformer = ColumnTransformer(
        transformers=[
            ('minmax_scaler', minmax_scaler, feature_columns)
        ]
    )

    pipeline = Pipeline([
        ('feature_engineer', FeatureEngineer()),
        ('imputer', SimpleImputer(strategy='mean')),
        ('column_transformer', column_transformer),
    ])

    pipeline.set_output(transform="pandas")

    out_df = pipeline.fit_transform(df)
    target = target_scaler.fit_transform(df[target_columns].values.reshape(-1, 1))
    out_df[target_columns] = target

    # TODO: Save pipeline with mlflow

    return out_df


def create_windows(df, window_size, prediction_horizon, target_column='european_aqi'):
    data = df.to_numpy()
    target_index = df.columns.get_loc(target_column)

    X, y = [], []
    for i in range(len(data) - window_size - prediction_horizon + 1):
        X.append(data[i:i+window_size, :])
        y.append(data[i+window_size:i+window_size+prediction_horizon, target_index])
    return np.array(X), np.array(y)


def train_eval_model(city):
    df = read_csv(f"{DATA_PROCESSED_DIR}/{city}.csv")
    df = preprocess_data(df)
    X, y = create_windows(df, 24, 24)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=666)

    model = create_model(X_train.shape[1], X_train.shape[2])


def train_model(city):
    pass


def main():
    for city in get_cities():
        train_eval_model(city)
        # train_model(city)


if __name__ == '__main__':
    main()
