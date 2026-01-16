import os
from flask import Flask, session, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_migrate import Migrate
from flask_mail import Mail
from config import DevelopmentConfig 
from datetime import datetime

# Inisialisasi Extension (Global)
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()

def create_app(config_class=DevelopmentConfig):
    # 1. Membuat instance Flask
    app = Flask(__name__)
    
    # 2. Load Konfigurasi (Mengambil dari config.py)
    app.config.from_object(config_class)

    # --- CEK KONFIGURASI UPLOAD (DEBUGGING) ---
    # Ini akan muncul di terminal saat Anda menjalankan flask run
    # Pastikan angkanya sekitar 209715200 (untuk 200MB)
    max_size = app.config.get('MAX_CONTENT_LENGTH')
    print(f"Status Config: Batas Upload Saat Ini adalah {max_size} bytes")
    # ------------------------------------------

    # 3. Inisialisasi Extension ke dalam App
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    
    # Konfigurasi Login Manager
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Sesi Anda telah berakhir karena tidak aktif. Silakan login kembali."
    login_manager.login_message_category = "warning"

    # --- ERROR HANDLER: FILE TERLALU BESAR (413) ---
    # Menangani error jika file > MAX_CONTENT_LENGTH agar tidak crash
    @app.errorhandler(413)
    def request_entity_too_large(error):
        flash('Ukuran file terlalu besar! Harap kurangi ukuran atau durasi video (Max 200MB).', 'danger')
        return redirect(request.referrer or url_for('main.index'))

    # 4. Filter Waktu Custom untuk Jinja Template
    from app.utils import to_wib, format_wib
    
    app.jinja_env.filters["to_wib"] = to_wib
    app.jinja_env.filters["format_wib"] = format_wib
    
    def format_wib_date_only(value):
        if value is None: return ""
        wib_time = to_wib(value)
        return wib_time.strftime('%d %b %Y') 
    
    def format_wib_time_only(value):
        if value is None: return ""
        wib_time = to_wib(value)
        return wib_time.strftime('%H:%M')

    app.jinja_env.filters["format_wib_date_only"] = format_wib_date_only
    app.jinja_env.filters["format_wib_time_only"] = format_wib_time_only

    # 5. Registrasi Blueprint
    from app.auth import bp as auth_bp
    from app.main import bp as main_bp
    from app.reports import bp as reports_bp
    from app.admin import bp as admin_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(main_bp)
    app.register_blueprint(reports_bp, url_prefix="/reports")
    app.register_blueprint(admin_bp, url_prefix="/admin")

    # 6. User Loader & Logic Session
    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        if user_id is not None:
            return User.query.get(int(user_id))
        return None

    @app.before_request
    def before_request_callback():
        # A. LOGIKA AUTO LOGOUT (Sliding Session)
        # Memaksa sesi menggunakan durasi dari config (10 menit)
        session.permanent = True
        
        # Memaksa browser memperbarui cookie expiration time setiap request
        # Ini penting agar timer 10 menit di-reset saat user aktif klik menu
        session.modified = True 

        # B. Update Last Seen di Database
        if current_user.is_authenticated:
            current_user.last_seen = datetime.utcnow()
            try:
                db.session.commit()
            except:
                db.session.rollback()

    @app.after_request
    def add_header(response):
        """Mencegah browser caching halaman sensitif setelah logout"""
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0, private"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response

    # 7. Create Tables
    with app.app_context():
        db.create_all()

    return app