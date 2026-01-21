from app import db
from sqlalchemy import func
from datetime import datetime, timezone


class Laporan(db.Model):
    __tablename__ = "laporan"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    kode_pelaporan = db.Column(db.String(30), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    judul = db.Column(db.String(150), nullable=False)
    kategori_id = db.Column(db.Integer, db.ForeignKey("kategori.id"), nullable=False)

    lokasi = db.Column(db.String(200), nullable=False)
    wilayah = db.Column(db.String(100), nullable=True)
    deskripsi = db.Column(db.Text, nullable=False)

    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)

    prioritas = db.Column(db.Enum("normal", "tinggi"), default="normal")
    status = db.Column(
        db.Enum("diajukan", "diproses", "selesai", "ditolak", name="status_laporan"),
        default="diajukan",
        nullable=False,
    )

    # keterangan & waktu tiap status
    ringkasan_hasil = db.Column(db.Text, nullable=True)
    alasan_ditolak = db.Column(db.Text, nullable=True)
    tgl_diproses = db.Column(db.DateTime, nullable=True)
    tgl_selesai = db.Column(db.DateTime, nullable=True)
    tgl_ditolak = db.Column(db.DateTime, nullable=True)

    foto_path = db.Column(db.String(255), nullable=True)
    foto_admin = db.Column(db.String(255), nullable=True)


    created_at = db.Column(db.DateTime, default=func.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=func.now(timezone.utc), onupdate=func.now(timezone.utc))

    def __repr__(self):
        return f"<Laporan {self.kode_pelaporan}>"

    @staticmethod
    def generate_kode(user_id: int) -> str:
        timestamp = int(datetime.now(timezone.utc).timestamp())
        return f"LPR-{user_id}-{timestamp}"
