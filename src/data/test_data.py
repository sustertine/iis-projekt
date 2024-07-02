import os

import pandas as pd
from evidently.metric_preset import DataDriftPreset
from evidently.report import Report
from evidently.test_suite import TestSuite
from evidently.tests import TestNumberOfColumnsWithMissingValues, TestNumberOfRowsWithMissingValues, \
    TestNumberOfConstantColumns, TestNumberOfDuplicatedRows, TestNumberOfDuplicatedColumns, TestColumnsType, \
    TestNumberOfDriftedColumns

from evidently.test_preset import DataStabilityTestPreset, NoTargetPerformanceTestPreset

from src.util.constants import DATA_PROCESSED_DIR, DATA_REFERENCE_DIR, REPORTS_DIR


def data_drift_test():
    for file in os.listdir(f'{DATA_PROCESSED_DIR}'):
        report = Report(metrics=[DataDriftPreset()])
        filename = file.split('.')[0]

        current = pd.read_csv(f'{DATA_PROCESSED_DIR}/{file}')
        reference = pd.read_csv(f'{DATA_REFERENCE_DIR}/{file}')

        report.run(reference_data=reference, current_data=current)
        report.save_html(f'{REPORTS_DIR}/data-drift/{filename}.html')


def stability_test():
    for file in os.listdir(f'{DATA_PROCESSED_DIR}'):
        suite = TestSuite(tests=[
            TestNumberOfColumnsWithMissingValues(),
            TestNumberOfRowsWithMissingValues(),
            TestNumberOfConstantColumns(),
            TestNumberOfDuplicatedRows(),
            TestNumberOfDuplicatedColumns(),
            TestColumnsType(),
            TestNumberOfDriftedColumns(),
            NoTargetPerformanceTestPreset(),
            DataStabilityTestPreset()
        ])
        filename = file.split('.')[0]

        current = pd.read_csv(f'{DATA_PROCESSED_DIR}/{file}')
        reference = pd.read_csv(f'{DATA_REFERENCE_DIR}/{file}')

        suite.run(reference_data=reference, current_data=current)
        suite.save_html(f'{REPORTS_DIR}/data-stability/{filename}.html')


def main():
    data_drift_test()
    stability_test()


if __name__ == '__main__':
    main()
