from app import db

class Kategori(db.Model):
    __tablename__ = 'kategori'

    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), unique=True, nullable=False)
    deskripsi = db.Column(db.String(255), nullable=True)

    laporan = db.relationship('Laporan', backref='kategori', lazy=True)

    def __repr__(self):
        return f"<Kategori {self.nama}>"
