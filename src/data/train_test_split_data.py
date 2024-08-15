import os

import pandas as pd

from src.util.constants import DATA_PROCESSED_DIR, DATA_TRAIN_DIR, DATA_TEST_DIR


def time_series_split(df, test_size=0.2):
    train_size = int(len(df) * (1 - test_size))
    train, test = df[:train_size], df[train_size:]
    return train, test


def main():
    for file in os.listdir(f'{DATA_PROCESSED_DIR}'):
        df = pd.read_csv(f'{DATA_PROCESSED_DIR}/{file}')
        train, test = time_series_split(df, test_size=0.2)
        train.to_csv(f'{DATA_TRAIN_DIR}/{file}', index=False)
        test.to_csv(f'{DATA_TEST_DIR}/{file}', index=False)


if __name__ == '__main__':
    main()
