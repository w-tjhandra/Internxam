import os
from pathlib import Path

from dotenv import load_dotenv


BACKEND_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BACKEND_DIR / ".env")

JWT_SECRET = os.environ.get("JWT_SECRET", "supersecret")
JWT_ALGO = "HS256"
TOKEN_CHARSET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
