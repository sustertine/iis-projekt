import os

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.getenv('GITHUB_WORKSPACE', '../../')
DATA_RAW_DIR = os.path.join(BASE_DIR, 'data/raw')
DATA_PROCESSED_DIR = os.path.join(BASE_DIR, 'data/processed')
AIR_QUALITY_URL = os.getenv('AIR_QUALITY_URL')
