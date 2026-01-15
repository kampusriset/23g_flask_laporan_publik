from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_migrate import Migrate
from flask_mail import Mail  # PENTING: Tambahkan ini untuk email
from config import config    # Import dictionary config
from datetime import datetime, timedelta
import os

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail() # Extension untuk kirim email

def create_app(config_class=DevelopmentConfig):
    app_dir = os.path.dirname(os.path.abspath(__file__))

    app = Flask(
        __name__,
        static_folder=os.path.join(app_dir, "static"),
        static_url_path="/static",
    )
    app.config.from_object(config_class)
    root_dir = os.path.dirname(app_dir)

    app = Flask(__name__)
    app.static_folder = os.path.join(root_dir, "static")
    app.static_url_path = "/static"
    app.config.from_object(config_class)

    # session timeout 10 menit
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=10)

    # Inisialisasi Extension ke dalam App
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app) # Init Mail
    
    # Konfigurasi Login Manager
    login_manager.init_app(app)
    login_manager.login_view = "auth.login" # Redirect jika belum login
    login_manager.login_message = "Silakan login untuk mengakses halaman ini."
    login_manager.login_message_category = "warning" # Agar alert berwarna kuning/merah

    # ---- Filter Waktu Custom untuk Jinja Template ----
    # Pastikan file app/utils.py sudah ada fungsinya
    from app.utils import to_wib, format_wib
    
    # Filter 1: Format lengkap (Tanggal + Jam)
    app.jinja_env.filters["to_wib"] = to_wib
    app.jinja_env.filters["format_wib"] = format_wib
    
    # Filter 2: Format Tanggal Saja (Menghindari error jinja tadi)
    def format_wib_date_only(value):
        if value is None: return ""
        wib_time = to_wib(value)
        return wib_time.strftime('%d %b %Y') # Contoh: 15 Jan 2026
    
    # Filter 3: Format Jam Saja
    def format_wib_time_only(value):
        if value is None: return ""
        wib_time = to_wib(value)
        return wib_time.strftime('%H:%M') # Contoh: 14:30

    # Daftarkan filter baru
    app.jinja_env.filters["format_wib_date_only"] = format_wib_date_only
    app.jinja_env.filters["format_wib_time_only"] = format_wib_time_only
    # --------------------------------------------------

    # Registrasi Blueprint (Modular Routes)
    from app.auth import bp as auth_bp
    from app.main import bp as main_bp
    from app.reports import bp as reports_bp
    from app.admin import bp as admin_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(main_bp) # Main biasanya root '/'
    app.register_blueprint(reports_bp, url_prefix="/reports")
    app.register_blueprint(admin_bp)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Update Last Seen setiap user melakukan request
    @app.before_request
    def update_last_seen():
        if current_user.is_authenticated:
            current_user.last_seen = datetime.now()
            db.session.commit()
        session.permanent = True # Agar session expired sesuai setting config

    # Cache Control (Mencegah tombol back browser menampilkan halaman login stlh logout)
    @app.after_request
    def add_header(response):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0, private"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response

    with app.app_context():
        db.create_all()

    return app