import os
from dotenv import load_dotenv

load_dotenv()

# From .env
TG_TOKEN = os.getenv("TG_TOKEN")

# From code
CHUNK_SIZE = 8192
JSON_MAPS_FOLDER = "./json_maps"
UPLOAD_FOLDER = "uploads"
TELEGRAM_API_HOST = "https://api.telegram.org"
