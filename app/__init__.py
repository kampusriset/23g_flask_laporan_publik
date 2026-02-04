import os
import time
from flask import Flask, session, request, redirect, url_for, flash, Request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user, logout_user
from flask_migrate import Migrate
from flask_mail import Mail
import sys
from pathlib import Path
from config import config
from datetime import datetime, timedelta, timezone

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()
class BigFormRequest(Request):
    max_form_memory_size = 200 * 1024 * 1024

def create_app(config_name=None):
    app = Flask(__name__)
    if config_name is None:
        config_name = os.environ.get("FLASK_CONFIG", "default")

    # Load class config yang sesuai (DevelopmentConfig / ProductionConfig)
    app.config.from_object(config[config_name])
    
    # Opsional: Print biar lu tau lagi jalan di mode apa pas terminal nyala
    print(f"🚀 App Running in Mode: {config_name.upper()}")
    app.request_class = BigFormRequest
    # Pakai batas idle 10 menit (boleh override nilai dari config kalau mau)
    def check_requirements():
        """Validasi environment sebelum aplikasi running."""
        # 1. Cek Versi Python (Minimal 3.9 buat Pillow 10+)
        # Kita pake (3, 9) biar aman sesuai spek requirements lo
        if sys.version_info < (3, 10):
            print("❌ Error: Aplikasi ini butuh Python 3.9 atau lebih baru!")
            sys.exit(1)
        
        # 2. Cek Folder Static & Uploads
        UPLOAD_PATH = Path(app.root_path) / "static" / "uploads" / "laporan_foto"
        if not UPLOAD_PATH.exists():
            print(f"⚠️ Warning: Folder uploads tidak ditemukan. Membuat: {UPLOAD_PATH}")
            UPLOAD_PATH.mkdir(parents=True, exist_ok=True)
        
        print(f"✅ Environment Check: Python {sys.version.split()[0]} Detected. Gaspol!")
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=10)
    app.config["SESSION_REFRESH_EACH_REQUEST"] = False

    max_size = app.config.get("MAX_CONTENT_LENGTH")
    print(f"Status Config: Batas Upload Saat Ini adalah {max_size} bytes")

    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = (
        "Sesi Anda telah berakhir karena tidak aktif. Silakan login kembali."
    )
    login_manager.login_message_category = "warning"

    # ===============================
    # ERROR HANDLER (413)
    # ===============================
    @app.errorhandler(413)
    def request_entity_too_large(error):
        flash(
            "Ukuran file terlalu besar! Harap kurangi ukuran atau durasi video (Max 200MB).",
            "danger",
        )
        return redirect(request.referrer or url_for("main.index"))

    # ===============================
    # FILTER JINJA
    # ===============================
    from app.utils import to_wib, format_wib

    app.jinja_env.filters["to_wib"] = to_wib
    app.jinja_env.filters["format_wib"] = format_wib

    def format_wib_date_only(value):
        if not value:
            return ""
        return to_wib(value).strftime("%d %b %Y")

    def format_wib_time_only(value):
        if not value:
            return ""
        return to_wib(value).strftime("%H:%M")

    app.jinja_env.filters["format_wib_date_only"] = format_wib_date_only
    app.jinja_env.filters["format_wib_time_only"] = format_wib_time_only

    # ===============================
    # REGISTER BLUEPRINT
    # ===============================
    from app.auth import bp as auth_bp
    from app.main import bp as main_bp
    from app.reports import bp as reports_bp
    from app.admin import bp as admin_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(main_bp)
    app.register_blueprint(reports_bp, url_prefix="/reports")
    app.register_blueprint(admin_bp, url_prefix="/admin")

    # ===============================
    # USER LOADER
    # ===============================
    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id)) if user_id else None

    # ===============================
    # AUTO LOGOUT (IDLE TIME)
    # ===============================
    @app.before_request
    def before_request_callback():
        # Abaikan file static
        if request.endpoint and request.endpoint.startswith("static"):
            return

        if current_user.is_authenticated:
            now = time.time()
            last_activity = session.get("last_activity")

            # kalau session baru (last_activity hilang), set dari sekarang
            if last_activity is None:
                session["last_activity"] = now
                last_activity = now

            idle_time = now - last_activity
            # print("IDLE:", idle_time)  # aktifkan lagi kalau perlu debug

            if idle_time > app.permanent_session_lifetime.total_seconds():
                logout_user()
                session.clear()
                flash(
                    "Sesi Anda telah berakhir karena tidak aktif selama 10 menit.",
                    "warning",
                )
                return redirect(url_for("auth.login"))

            # reset timer setelah lolos pengecekan
            session["last_activity"] = now

            # opsional: catat last_seen user
            current_user.last_seen = datetime.now(timezone.utc)
            try:
                db.session.commit()
            except Exception:
                db.session.rollback()

    # ===============================
    # MENCEGAH CACHE SETELAH LOGOUT
    # ===============================
    @app.after_request
    def add_header(response):
        response.headers["Cache-Control"] = (
            "no-store, no-cache, must-revalidate, max-age=0, private"
        )
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response

    # ===============================
    # CREATE TABLE
    # ===============================
    with app.app_context():
       check_requirements()

    return app
