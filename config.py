import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "laporin-super-secret-key-2025-change-this!"

    # Dipakai sebagai batas idle 10 menit di before_request
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=1)
    SESSION_REFRESH_EACH_REQUEST = False  # biar Flask tidak auto-refresh expiry

    # Remember-me (kalau suatu saat mau dipakai di login, sekarang remember=False)
    REMEMBER_COOKIE_DURATION = timedelta(days=7)
    REMEMBER_COOKIE_REFRESH_EACH_REQUEST = True

    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:@localhost/pelaporan_fasilitas"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.path.join(basedir, "app/static/uploads")
    MAX_CONTENT_LENGTH = 200 * 1024 * 1024
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "pdf", "mp4"}

    RATELIMIT_ENABLED = True
    RATELIMIT_DEFAULT = "200 per day"
    RATELIMIT_STORAGE_URL = "memory://"

    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.googlemail.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "true").lower() in ["true", "on", "1"]
    MAIL_USE_SSL = os.environ.get("MAIL_USE_SSL", "false").lower() in ["true", "on", "1"]
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER", "LaporIN <noreply@laporin.id>")

    TIMEZONE = "Asia/Jakarta"


class DevelopmentConfig(Config):
    DEBUG = True

    if os.environ.get("DB_TYPE") == "mysql":
        SQLALCHEMY_DATABASE_URI = (
            f"mysql+pymysql://{os.environ.get('DB_USER')}:{os.environ.get('DB_PASS')}"
            f"@{os.environ.get('DB_URI')}:{os.environ.get('DB_PORT')}/{os.environ.get('DB_NAME')}"
        )


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    MAIL_SUPPRESS_SEND = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


class ProductionConfig(Config):
    DEBUG = False
    _db_user = os.environ.get("DB_USER")
    _db_pass = os.environ.get("DB_PASS", "")
    _db_host = os.environ.get("DB_URI", "localhost")
    _db_port = os.environ.get("DB_PORT", "3306")
    _db_name = os.environ.get("DB_NAME")
    if os.environ.get("DATABASE_URL"):
        SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    elif _db_user and _db_name:
        SQLALCHEMY_DATABASE_URI = (
            f"mysql+pymysql://{_db_user}:{_db_pass}@{_db_host}:{_db_port}/{_db_name}"
        )
    else:
        # Fallback terakhir biar gak crash (opsional)
        SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "prod_fallback.sqlite")
    
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
