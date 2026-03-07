import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Token (Get from @BotFather)
BOT_TOKEN = os.getenv("TOKEN")

# Base URL for NestJS API
API_BASE_URL = os.getenv("BACKEND_URL")

# List of admin Telegram IDs
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS").split(","))) # Add your ID here
