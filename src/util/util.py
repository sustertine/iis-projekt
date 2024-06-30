from src.util.constants import BASE_DIR

import json

def get_all_cities():
    with open(BASE_DIR + '/resources/cities.json') as f:
        data = json.load(f)
        return list(data.keys())

def get_all_coordinates():
    with open(BASE_DIR + '/resources/cities.json') as f:
        data = json.load(f)
        return dict(data)