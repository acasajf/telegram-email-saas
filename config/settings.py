import os
from dotenv import load_dotenv

load_dotenv()

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# Redis
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)

# PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL", "")

# SST Finder API
SST_FINDER_URL = os.getenv("SST_FINDER_URL", "http://localhost:3000")

# FastAPI
API_PORT = int(os.getenv("API_PORT", "8000"))

# Redis channel
NOTIFICATION_CHANNEL = "sst:notifications"
