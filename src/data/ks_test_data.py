import os

import pandas as pd
from scipy.stats import kstest

from src.util.constants import DATA_PROCESSED_DIR, DATA_REFERENCE_DIR


def main():
    for file in os.listdir(f'{DATA_PROCESSED_DIR}'):
        current = pd.read_csv(f'{DATA_PROCESSED_DIR}/{file}')
        reference = pd.read_csv(f'{DATA_REFERENCE_DIR}/{file}')

        print('-' * 50)
        print(f'KS test for file {file}')
        print('-' * 50)
        for column in current.columns.drop('time'):
            D, p_value = kstest(current[column], reference[column])
            print(f'\t- D = {D}, p-value = {p_value} ({column})')

        print('-' * 50, end='\n\n')


if __name__ == '__main__':
    main()
