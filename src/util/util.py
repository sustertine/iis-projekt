from src.util.constants import BASE_DIR

import json


def get_city_names():
    with open(BASE_DIR + '/resources/cities.json') as f:
        data = json.load(f)
        return list(data.keys())


def get_cities_and_coordinates():
    with open(BASE_DIR + '/resources/cities.json') as f:
        data = json.load(f)
        return dict(data)
