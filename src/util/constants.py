import os

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.getenv('GITHUB_WORKSPACE', '../../')
DATA_RAW_DIR = os.path.join(BASE_DIR, 'data/raw')
DATA_PROCESSED_DIR = os.path.join(BASE_DIR, 'data/processed')
DATA_REFERENCE_DIR = os.path.join(BASE_DIR, 'data/reference')
AIR_QUALITY_URL = os.getenv('AIR_QUALITY_URL')
WEATHER_URL = os.getenv('WEATHER_URL')
