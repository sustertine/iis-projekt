import logging
import os

import tensorflow as tf
import pickle as pkl
import json

from keras import Sequential
from keras.layers import LSTM, Dense

import numpy as np
import pandas as pd
from mlflow.environment_variables import MLFLOW_TRACKING_URI
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler

from src.models.feature_engineer import FeatureEngineer
from src.util.constants import RESOURCES_DIR, DATA_PROCESSED_DIR, MODELS_DIR, MLFLOW_REPO_OWNER, MLFLOW_REPO_NAME, \
    MLFLOW_TRACKING_USERNAME, MLFLOW_TRACKING_PASSWORD

import dagshub
import mlflow

dagshub.init(repo_owner=MLFLOW_REPO_OWNER,
             repo_name=MLFLOW_REPO_NAME,
             mlflow=True)

mlflow.set_tracking_uri(os.getenv('MLFLOW_TRACKING_URI'))
os.environ['MLFLOW_TRACKING_USERNAME'] = MLFLOW_TRACKING_USERNAME
os.environ['MLFLOW_TRACKING_PASSWORD'] = MLFLOW_TRACKING_PASSWORD

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(threadName)s/%(lineno)s] - %(levelname)s - %(message)s'
)


def create_model(n_time_steps, n_features):
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


def preprocess_data(df, city, save_models=False):
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

    if save_models:
        path = f'{MODELS_DIR}/{city}'
        if not os.path.exists(path):
            os.makedirs(path)
        pkl.dump(pipeline, open(f'{MODELS_DIR}/{city}/pipeline.pkl', 'wb'))
        pkl.dump(target_scaler, open(f'{MODELS_DIR}/{city}/target_scaler.pkl', 'wb'))

        mlflow.sklearn.log_model(pipeline, f'{city}_pipeline')
        mlflow.register_model(f'runs:/{mlflow.active_run().info.run_id}/{city}_pipeline', f'{city}_pipeline')
        mlflow.sklearn.log_model(target_scaler, f'{city}_target_scaler')
        mlflow.register_model(f'runs:/{mlflow.active_run().info.run_id}/{city}_target_scaler', f'{city}_target_scaler')

    return out_df


def create_windows(df, window_size, prediction_horizon, target_column='european_aqi'):
    data = df.to_numpy()
    target_index = df.columns.get_loc(target_column)

    X, y = [], []
    for i in range(len(data) - window_size - prediction_horizon + 1):
        X.append(data[i:i + window_size, :])
        y.append(data[i + window_size:i + window_size + prediction_horizon, target_index])
    return np.array(X), np.array(y)


def train_eval_model(city, epochs):
    logging.info(f'Training and evaluating model for city: {city}')
    df = read_csv(f"{DATA_PROCESSED_DIR}/{city}.csv")
    df = preprocess_data(df, city, False)
    X, y = create_windows(df, 24, 24)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=666)

    model = create_model(X_train.shape[1], X_train.shape[2])
    model.fit(X_train, y_train, epochs=epochs, batch_size=32, validation_data=(X_test, y_test), verbose=2)


def train_model(city, epochs):
    logging.info(f'Training model for city: {city}')
    df = read_csv(f"{DATA_PROCESSED_DIR}/{city}.csv")
    df = preprocess_data(df, city, True)
    X, y = create_windows(df, 24, 24)

    model = create_model(X.shape[1], X.shape[2])
    model.fit(X, y, epochs=epochs, batch_size=32, verbose=2)

    model.save(f"{MODELS_DIR}/{city}/model.h5")
    mlflow.log_artifact(f"{MODELS_DIR}/{city}/model.h5")
    mlflow.register_model(f'runs:/{mlflow.active_run().info.run_id}/{city}/model', f'{city}_model')


def main():
    for city in get_cities():
        mlflow.set_experiment('Train models')
        with mlflow.start_run(run_name=city):
            mlflow.tensorflow.autolog()
            train_eval_model(city, epochs=3)
            train_model(city, epochs=3)


if __name__ == '__main__':
    main()
