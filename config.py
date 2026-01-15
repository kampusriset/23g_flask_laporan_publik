import os
from dotenv import load_dotenv
load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "laporin-super-secret-key-2025-change-this!"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "sqlite:///laporin.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


    # Email settings
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 465))
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER", "LaporIN <no-reply@laporin.local>")


class DevelopmentConfig(Config):
    DEBUG = os.environ.get("DEBUG", "true").lower() in ["true", "1", "t"]
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DATABASE_URL")
        or f"mysql+pymysql://{os.environ.get('DB_USER')}:{os.environ.get('DB_PASS')}"
           f"@{os.environ.get('DB_URI')}:{os.environ.get('DB_PORT')}/{os.environ.get('DB_NAME')}"
    )


class ProductionConfig(Config):
    DEBUG = False
