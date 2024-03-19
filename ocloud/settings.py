import os
from dotenv import load_dotenv

load_dotenv()

# Filling parameters
TG_TOKEN = os.getenv("TG_TOKEN")
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER")
