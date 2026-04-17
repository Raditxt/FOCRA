import os
from dotenv import load_dotenv

load_dotenv()

APP_NAME = "Focra"
APP_VERSION = "0.1.0"
DB_PATH = "data/focra.db"
OLLAMA_MODEL = "llama3.1:8b"
OLLAMA_HOST = "http://localhost:11434"