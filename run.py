from app import create_app
from app.models import db

app = create_app()

from flask.cli import with_appcontext
from app import db # Sesuaikan dengan lokasi db lo
from app.models import User, Kategori # Import modelnya
from werkzeug.security import generate_password_hash
from datetime import datetime, timezone
@app.cli.command("seed-db")
@with_appcontext
def seed_db():
    """Seed data awal: Kategori & Admin."""
    
    # --- 1. SEED KATEGORI ---
    print("⏳ Lagi nanam data kategori...")
    data_kategori = [
        {'id': 1, 'nama': 'Jalan Rusak', 'deskripsi': 'Kerusakan jalan raya, trotoar, lubang, atau permukaan bergelombang.'},
        {'id': 2, 'nama': 'Lampu Jalan', 'deskripsi': 'Lampu penerangan jalan umum mati, redup, atau rusak.'},
        {'id': 3, 'nama': 'Sampah & Kebersihan', 'deskripsi': 'Penumpukan sampah, TPS liar, lingkungan kotor.'},
        {'id': 4, 'nama': 'Fasilitas Umum', 'deskripsi': 'Kerusakan taman, halte, trotoar, jembatan penyeberangan, dsb.'},
        {'id': 5, 'nama': 'Drainase & Banjir', 'deskripsi': 'Saluran air tersumbat, genangan, atau banjir lokal.'},
    ]

    for kat in data_kategori:
        existing_kat = Kategori.query.get(kat['id'])
        if not existing_kat:
            new_kat = Kategori(id=kat['id'], nama=kat['nama'], deskripsi=kat['deskripsi'])
            db.session.add(new_kat)
    
    # --- 2. SEED ADMIN ---
    print("⏳ Lagi spawn admin kece...")
    existing_user = User.query.filter_by(username='admin').first()
    if not existing_user:
        admin = User(
            nama_lengkap="Administrator Utama",
            username="admin",
            email="admin@bilikku.my.id",
            phone="08123456789",
            password_hash=generate_password_hash("laporinaja531"),
            role="admin",
	    created_at=datetime.now(timezone.utc),
            is_active=True
        )
        db.session.add(admin)
    else:
        print("⚠️ Admin udah ada, skip!")

    try:
        db.session.commit()
        print("✅ Mantap! Database udah terisi. Gaspol!")
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error pas seeding: {e}") 

if __name__ == '__main__':
    
    app.run(debug=True,host='0.0.0.0', port=5000)
