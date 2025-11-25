from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    nama_lengkap = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    no_telp = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default='user', nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    laporans = db.relationship('Laporan', backref='user', lazy=True, foreign_keys='Laporan.username', primaryjoin='User.username == Laporan.username')

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        self.password = generate_password_hash(password, method='pbkdf2:sha256')


    def check_password(self, password):
        if not self.password or self.password.strip() == "" or "pbkdf2" not in self.password:
            return False
        return check_password_hash(self.password, password)

class Laporan(db.Model):
    __tablename__ = 'laporan'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    judul = db.Column(db.String(100), nullable=False)
    deskripsi = db.Column(db.Text, nullable=False)
    lokasi = db.Column(db.String(150), nullable=False)
    alamat = db.Column(db.Text, nullable=True)
    foto = db.Column(db.Text, nullable=True)  # path/nama file
    status = db.Column(db.String(20), nullable=True)
    tanggal = db.Column(db.DateTime, nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    kode_pos = db.Column(db.String(20), nullable=True)
    username = db.Column(db.String(50), db.ForeignKey('users.username'), nullable=True)

    def __repr__(self):
        return f"<Laporan {self.judul} oleh {self.username}>"
class Kategori(db.Model):
    __tablename__ = 'kategori'
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False, unique=True)
    
    def __repr__(self):
        return f"<Kategori {self.nama}>"
