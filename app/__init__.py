from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_migrate import Migrate
from config import DevelopmentConfig
from datetime import datetime, timedelta
import os

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()


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

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Login dulu ya!"

    # ---- Filter waktu WIB untuk Jinja ----
    from app.utils import to_wib, format_wib

    app.jinja_env.filters["to_wib"] = to_wib
    app.jinja_env.filters["format_wib"] = format_wib
    # --------------------------------------

    from app.models import User, Laporan, Kategori
    from app.auth import bp as auth_bp
    from app.main import bp as main_bp
    from app.reports import bp as reports_bp
    from app.admin import bp as admin_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(main_bp)
    app.register_blueprint(reports_bp, url_prefix="/reports")
    app.register_blueprint(admin_bp)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.before_request
    def update_last_seen():
        if current_user.is_authenticated:
            current_user.last_seen = datetime.utcnow()
            db.session.commit()
        session.permanent = True
        session.modified = True

    @app.after_request
    def add_header(response):
        response.headers["Cache-Control"] = (
            "no-store, no-cache, must-revalidate, max-age=0, private"
        )
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response

    with app.app_context():
        db.create_all()
        print("Database tables created!")

    return app
