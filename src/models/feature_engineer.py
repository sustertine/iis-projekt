from sklearn.base import BaseEstimator, TransformerMixin


class FeatureEngineer(BaseEstimator, TransformerMixin):
    def __init__(self):
        pass

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X = X.copy()

        X['temperature_variability'] = X['temperature_2m'].rolling(window=3).std()
        X['temperature_variability'] = X['temperature_variability'].bfill()

        X['humidity_adjusted_temp'] = X['temperature_2m'] * (1 + X['relative_humidity_2m'])
        X['air_quality_combined'] = (X['pm10'] + X['pm2_5'] + X['nitrogen_dioxide'] +
                                     X['sulphur_dioxide'] + X['ozone']) / 5
        X['precipitation_wind_interaction'] = X['precipitation_probability'] * X[
            'wind_speed_10m']
        X['pollutant_range'] = X[['pm10', 'pm2_5', 'nitrogen_dioxide', 'sulphur_dioxide', 'ozone']].max(axis=1) - X[
            ['pm10', 'pm2_5', 'nitrogen_dioxide', 'sulphur_dioxide', 'ozone']].min(axis=1)

        return X

    def set_output(self, *, transform=None):
        pass
