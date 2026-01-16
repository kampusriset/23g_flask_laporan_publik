import os
from dotenv import load_dotenv
from datetime import timedelta # <--- WAJIB DITAMBAHKAN (Agar pengaturan waktu jalan)

# Memuat environment variable dari file .env
load_dotenv()

# Mendapatkan direktori dasar proyek untuk absolute path
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # --- Security & Core ---
    # Gunakan key yang kuat di .env untuk produksi
    SECRET_KEY = os.environ.get("SECRET_KEY") or "laporin-super-secret-key-2025-change-this!"

    PERMANENT_SESSION_LIFETIME = timedelta(minutes=10)
    SESSION_REFRESH_EACH_REQUEST = False

    
    # Pengaturan Remember Me (opsional, jika dicentang)
    REMEMBER_COOKIE_DURATION = timedelta(days=7)
    REMEMBER_COOKIE_REFRESH_EACH_REQUEST = True
    
    # --- Database (MySQL) ---
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:@localhost/pelaporan_fasilitas"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    
    # --- Uploads ---
    # Menggunakan path absolute agar tidak error
    UPLOAD_FOLDER = os.path.join(basedir, "app/static/uploads")
    
    # UBAH DISINI: 200 MB (Agar video bisa masuk)
    # Rumus: 200 * 1024 * 1024
    MAX_CONTENT_LENGTH = 200 * 1024 * 1024  
    
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'mp4'} # Filter file

    # --- Rate Limiting ---
    RATELIMIT_ENABLED = True
    RATELIMIT_DEFAULT = "200 per day"
    RATELIMIT_STORAGE_URL = "memory://"

    # --- Email Settings (PENTING untuk Reset Password) ---
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.googlemail.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    # Logika otomatis: Port 465 pakai SSL, 587 pakai TLS
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "true").lower() in ["true", "on", "1"]
    MAIL_USE_SSL = os.environ.get("MAIL_USE_SSL", "false").lower() in ["true", "on", "1"]
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD") # App Password Gmail
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER", "LaporIN <noreply@laporin.id>")

    # --- Timezone ---
    TIMEZONE = 'Asia/Jakarta'


class DevelopmentConfig(Config):
    """Konfigurasi untuk lingkungan pengembangan"""
    DEBUG = True
    
    # Cek apakah mau pakai MySQL atau fallback ke SQLite
    if os.environ.get('DB_TYPE') == 'mysql':
        SQLALCHEMY_DATABASE_URI = (
            f"mysql+pymysql://{os.environ.get('DB_USER')}:{os.environ.get('DB_PASS')}"
            f"@{os.environ.get('DB_URI')}:{os.environ.get('DB_PORT')}/{os.environ.get('DB_NAME')}"
        )


class TestingConfig(Config):
    """Konfigurasi untuk testing otomatis"""
    TESTING = True
    WTF_CSRF_ENABLED = False  # Matikan CSRF saat testing form
    MAIL_SUPPRESS_SEND = True # Jangan kirim email beneran saat testing
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:' # Database di RAM (cepat & bersih)


class ProductionConfig(Config):
    """Konfigurasi untuk deploy produksi"""
    DEBUG = False
    
    # Gunakan database produksi (PostgreSQL/MySQL) yang kuat
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    
    # Security Cookies (Aktifkan ini jika sudah pakai HTTPS/SSL)
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
