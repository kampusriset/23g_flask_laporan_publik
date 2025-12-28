from app import create_app
from app.models import db

app = create_app()

@app.cli.command("seed-user")
def seed_user():
    """Seed data user pertama buat admin."""
    from app.models import User # Pastikan path import bener
    
    # Cek dulu biar nggak duplikat email/username
    existing_user = User.query.filter_by(username='admin').first()
    if existing_user:
        print("Username 'admin_kece' udah ada, nggak usah di-seed lagi ya.")
        return

    # Buat instance user baru
    new_user = User(
        nama_lengkap="Administrator Utama",
        username="admin",
        email="admin@vibes.com",
        phone="08123456789",
        role="admin",
        is_active=True
    )
    
    # WAJIB: Pake method set_password biar di-hash!
    new_user.set_password("admin123")
    
    db.session.add(new_user)
    db.session.commit()
    
    print("Mantap! Admin berhasil di-spawn. Silakan login!")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Database tables created!")
    app.run(debug=True,host='0.0.0.0', port=5000)
