from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / '.env')

OLLAMA_API_URL = os.getenv('OLLAMA_API_URL', 'http://127.0.0.1:11434/api/chat')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'lexi')
APP_HOST = os.getenv('APP_HOST', '127.0.0.1')
APP_PORT = int(os.getenv('APP_PORT', '8765'))
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./companion_lab.db')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
