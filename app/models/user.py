from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import datetime, timezone # <--- Import timezone
import pytz
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from flask import current_app

WIB = pytz.timezone("Asia/Jakarta")

class User(UserMixin, db.Model):
    # ... (kolom id, nama, dll sama aja) ...
    id = db.Column(db.Integer, primary_key=True)
    nama_lengkap = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(30), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20))
    role = db.Column(db.String(20), default='user')
    is_active = db.Column(db.Boolean, default=True)

    # --- BAGIAN WAKTU YANG DI-UPDATE ---
    
    # created_at: Pake func.now(timezone.utc) biar database (MySQL) yang nentuin jamnya (Lebih Akurat)
    created_at = db.Column(db.DateTime, default=func.now(timezone.utc))
    
    # last_seen: Pake lambda biar Python yang generate UTC Aware tiap kali data masuk
    last_seen = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    last_login_at = db.Column(db.DateTime)

    laporan = db.relationship("Laporan", backref="user", lazy=True)

    # ... (set_password & check_password sama) ...
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # --- IS ONLINE (LOGIC BARU) ---
    def is_online(self, minutes=5):
        if not self.last_seen:
            return False
        
        # Ambil waktu sekarang dalam UTC (Aware)
        now_utc = datetime.now(timezone.utc)
        
        # Masalah: MySQL tipe DATETIME itu "lupa" timezone pas disimpen.
        # Pas ditarik (self.last_seen), dia jadi 'naive' lagi.
        # Jadi kita harus pastiin last_seen itu dianggap UTC dulu.
        last_seen_aware = self.last_seen
        if last_seen_aware.tzinfo is None:
            last_seen_aware = last_seen_aware.replace(tzinfo=timezone.utc)

        delta = now_utc - last_seen_aware
        return delta.total_seconds() < minutes * 60

    # --- HELPER WIB ---
    def last_seen_wib(self):
        return self._to_wib(self.last_seen)

    def last_login_wib(self):
        return self._to_wib(self.last_login_at)

    # Bikin private helper biar gak ngulang kodingan
    def _to_wib(self, dt_value):
        if not dt_value:
            return None
        
        # 1. Pastikan dia UTC (karena dari DB biasanya naive)
        if dt_value.tzinfo is None:
            dt_value = pytz.utc.localize(dt_value)
            
        # 2. Convert ke WIB
        return dt_value.astimezone(WIB)

    # ... (get_reset_token sama aja) ...
    def get_reset_token(self):
        s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        return s.dumps({"user_id": self.id}, salt="password-reset-salt")
    
    @staticmethod
    def verify_reset_token(token, max_age=3600):
        s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        try:
            data = s.loads(token, max_age=max_age, salt="password-reset-salt")
        except (BadSignature, SignatureExpired):
            return None
        return User.query.get(data.get("user_id"))