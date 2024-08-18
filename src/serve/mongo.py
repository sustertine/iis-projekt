import os

from pymongo import MongoClient

from dotenv import load_dotenv

load_dotenv()


class ApiCallsClient:
    def __init__(self):
        self.client = MongoClient(os.getenv('MONGO_URL'))
        self.db = self.client['aqi-api-calls']
        self.api_calls = self.db['api-calls']

    def get_api_calls(self):
        entries = list(self.api_calls.find())

        for entry in entries:
            entry['_id'] = str(entry['_id'])
        return entries

    def get_api_calls_by_location(self, location_name):
        entries = list(self.api_calls.find({'location_name': location_name}))

        for entry in entries:
            entry['_id'] = str(entry['_id'])
        return entries

    def create_api_call(self, data):
        self.api_calls.insert_one(data)


