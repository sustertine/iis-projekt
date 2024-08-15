import os

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.getenv('GITHUB_WORKSPACE', '../../')
DATA_RAW_DIR = os.path.join(BASE_DIR, 'data/raw')
DATA_PROCESSED_DIR = os.path.join(BASE_DIR, 'data/processed')
DATA_REFERENCE_DIR = os.path.join(BASE_DIR, 'data/reference')
DATA_TRAIN_DIR = os.path.join(BASE_DIR, 'data/train')
DATA_TEST_DIR = os.path.join(BASE_DIR, 'data/test')
REPORTS_DIR = os.path.join(BASE_DIR, 'reports')
AIR_QUALITY_URL = os.getenv('AIR_QUALITY_URL')
WEATHER_URL = os.getenv('WEATHER_URL')
RESOURCES_DIR = os.path.join(BASE_DIR, 'resources')