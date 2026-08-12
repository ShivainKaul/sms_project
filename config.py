import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")
    MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/sms_db")
    MONGO_DB_NAME = os.environ.get("MONGO_DB_NAME", "sms_db")
