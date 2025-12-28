from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import datetime
import pytz


WIB = pytz.timezone("Asia/Jakarta")


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama_lengkap = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(30), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20))
    role = db.Column(db.String(20), default='user')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=func.now())
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    last_login_at = db.Column(db.DateTime)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    laporan = db.relationship("Laporan", backref="user", lazy=True)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_online(self, minutes=5):
        if not self.last_seen:
            return False
        delta = datetime.utcnow() - self.last_seen
        return delta.total_seconds() < minutes * 60

    def last_seen_wib(self):
        if not self.last_seen:
            return None
        utc = self.last_seen
        if utc.tzinfo is None:
            utc = pytz.utc.localize(utc)
        return utc.astimezone(WIB)
    
    def last_login_wib(self):
        if not self.last_login_at:
            return None
        utc = self.last_login_at
        if utc.tzinfo is None:
            utc = pytz.utc.localize(utc)
        return utc.astimezone(WIB)

