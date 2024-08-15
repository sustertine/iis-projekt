import json


def get_locations_info():
    location_info = json.load(open("resources/cities.json"))
    return [{"name": city, "lat": info["lat"], "lon": info["lon"]} for city, info in location_info.items()]
