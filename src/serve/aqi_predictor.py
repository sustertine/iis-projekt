from random import random


class AQIPredictor:

    def __init__(self):
        self.model_map = {}
        self.mms_map = {}
        self.target_mms_map = {}



    def predict(self, location_name: str):
        # Return 24 objects with key: aqi and value: random number and another key time with each being one hour later from the current time
        return [{"aqi": random(), "time": i} for i in range(24)]
