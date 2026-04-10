import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
APP_NAME = "Focra"
APP_VERSION = "0.1.0"
DB_PATH = "data/focra.db"
MODEL_NAME = "gemini-2.0-flash"
MAX_TOKENS = 1000