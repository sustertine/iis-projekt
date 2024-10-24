import concurrent
import logging
import os

import pickle as pkl
import json
import time

from keras import Sequential
from keras.layers import LSTM, Dense

import tensorflow as tf

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler

from src.models.feature_engineer import FeatureEngineer
from src.util.constants import RESOURCES_DIR, DATA_PROCESSED_DIR, MODELS_DIR, \
    MLFLOW_TRACKING_USERNAME, MLFLOW_TRACKING_PASSWORD

import mlflow

mlflow.set_tracking_uri(os.getenv('MLFLOW_TRACKING_URI'))
os.environ['MLFLOW_TRACKING_USERNAME'] = MLFLOW_TRACKING_USERNAME
os.environ['MLFLOW_TRACKING_PASSWORD'] = MLFLOW_TRACKING_PASSWORD

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(threadName)s/%(lineno)s] - %(levelname)s - %(message)s'
)


def create_model(n_time_steps, n_features):
    model = Sequential()
    model.add(LSTM(50, input_shape=(n_time_steps, n_features)))  # train_X.shape[1], train_X.shape[2]
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

    y_pred = model.predict(X_test)
    mlflow.log_metric('mae', np.mean(np.abs(y_test - y_pred)))
    mlflow.log_metric('mse', np.mean((y_test - y_pred) ** 2))
    mlflow.log_metric('rmse', np.sqrt(np.mean((y_test - y_pred) ** 2)))


def train_model(city, epochs):
    logging.info(f'Training model for city: {city}')
    df = read_csv(f"{DATA_PROCESSED_DIR}/{city}.csv")
    df = preprocess_data(df, city, True)
    X, y = create_windows(df, 24, 24)

    model = create_model(X.shape[1], X.shape[2])
    model.fit(X, y, epochs=epochs, batch_size=32, verbose=2)

    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    converter.target_spec.supported_ops = [
        tf.lite.OpsSet.TFLITE_BUILTINS,
        tf.lite.OpsSet.SELECT_TF_OPS
    ]
    converter._experimental_lower_tensor_list_ops = False
    tflite_model = converter.convert()

    with open(f"{MODELS_DIR}/{city}/model.tflite", "wb") as f:
        f.write(tflite_model)

    mlflow.log_artifact(f"{MODELS_DIR}/{city}/model.tflite")
    mlflow.register_model(f'runs:/{mlflow.active_run().info.run_id}/{city}/model', f'{city}_model_tflite')


def process_city(city):
    mlflow.set_experiment('Train models')
    with mlflow.start_run(run_name=city):
        mlflow.tensorflow.autolog()
        train_eval_model(city, epochs=3)
        train_model(city, epochs=3)


def main():
    start_time = time.time()
    cities = list(get_cities())

    for city in cities:
        process_city(city)

    end_time = time.time()
    execution_time = end_time - start_time
    logging.info(f'Models trained in: {execution_time / 60}min {execution_time % 60:.2f}s')


if __name__ == '__main__':
    main()
