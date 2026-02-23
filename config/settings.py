import os 
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Alert thresholdsclear 
UMBRAL_DISCO_MIN_PCT = 15.0 # Alert if less than 15% remains
UMBRAL_LOG_MAX_PCT = 85.0   # Alert if log exceeds 85% 
SQL_TIMEOUT = 10         
