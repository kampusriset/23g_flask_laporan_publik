from functools import wraps
from datetime import datetime
import re

from flask import (
    Flask, render_template, request, redirect, url_for, flash,
    abort, jsonify, make_response, session
)
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, login_user, login_required,
    logout_user, current_user
)
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from models.laporan_model import db, User, Laporan
from flask_login import logout_user, current_user
from flask import session, flash, redirect, url_for
from flask_login import UserMixin
from models.laporan_model import Kategori


# ===============================================================
# DEKORATOR NO-CACHE
# ===============================================================
def nocache(view):
    @wraps(view)
    def no_cache_view(*args, **kwargs):
        resp = make_response(view(*args, **kwargs))
        resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        resp.headers['Pragma'] = 'no-cache'
        resp.headers['Expires'] = '0'
        return resp
    return no_cache_view

# ===============================================================
# INISIALISASI APP & EKSTENSI
# jika pakai password dibelakang root misal root:1234 
# ===============================================================
app = Flask(__name__)
app.config.update(
    SECRET_KEY='rahasia_laporin_2025_super_aman_123!',
    SQLALCHEMY_DATABASE_URI='mysql+mysqlconnector://root:@localhost/pelaporan_fasilitas',
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    SQLALCHEMY_ENGINE_OPTIONS={'pool_pre_ping': True, 'pool_recycle': 300}
)

serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
login_manager = LoginManager()

db.init_app(app)
login_manager.init_app(app)

login_manager.login_view = 'login'
login_manager.login_message = 'Silakan login terlebih dahulu.'
login_manager.login_message_category = 'warning'

# ===============================================================
# USER LOADER
# ===============================================================
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ===============================================================
# AUTO CREATE DB + ADMIN DEFAULT
# ===============================================================
with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        admin = User(
            nama_lengkap='Administrator',
            username='admin',
            email='admin@laporin.id',
            no_telp='081234567890',
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("Admin default dibuat: username=admin, password=admin123")

# ===============================================================
# HELPERS
# ===============================================================
def get_landing_stats():
    """
    Ambil statistik yang dibutuhkan landing page (dipakai oleh '/' dan '/<page>')
    Mengembalikan: total_users, laporan_labels, laporan_data
    """
    total_users = User.query.count()

    laporan_stats = (
        db.session.query(
            func.extract('year', Laporan.tanggal).label('tahun'),
            func.extract('month', Laporan.tanggal).label('bulan'),
            func.count().label('jumlah')
        )
        .group_by(func.extract('year', Laporan.tanggal), func.extract('month', Laporan.tanggal))
        .order_by(func.extract('year', Laporan.tanggal), func.extract('month', Laporan.tanggal))
        .all()
    )

    # laporan_stats menghasilkan (tahun, bulan, jumlah)
    labels = [f"{int(bulan)}/{int(tahun)}" for tahun, bulan, jumlah in laporan_stats]
    data = [int(jumlah) for tahun, bulan, jumlah in laporan_stats]

    return total_users, labels, data

# ===============================================================
# ROUTES
# ===============================================================

# Halaman Landing (root)
@app.route('/')
@nocache
def landing():
    print('>> AUTH:', current_user.is_authenticated, getattr(current_user, "email", "-"))
    total_users, labels, data = get_landing_stats()
    return render_template(
        'landing.html',
        total_users=total_users,
        laporan_labels=labels,
        laporan_data=data,
        goto=None
    )

# Route dinamis agar /tentang, /features, /alur, /kontak, dsb tetap menampilkan landing.html
@app.route('/<page>')
@nocache
def landing_sections(page):
    valid = {
        'home': 'home',
        'features': 'features',
        'statistik': 'statistik',
        'alur': 'alur',
        'tentang': 'tentang',
        'kontak': 'kontak',
    }

    total_users, labels, data = get_landing_stats()
    if page.lower() in valid:
        return render_template(
            'landing.html',
            total_users=total_users,
            laporan_labels=labels,
            laporan_data=data,
            goto=page.lower()
        )

    return render_template(
        'landing.html',
        total_users=total_users,
        laporan_labels=labels,
        laporan_data=data,
        goto=None
    )

# ===============================================================
# REGISTER
# ===============================================================
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('landing'))

    if request.method == 'POST':
        nama_lengkap = request.form.get('nama_lengkap', '').strip()
        username = request.form.get('username', '').strip().lower()
        no_telp = request.form.get('no_telp', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        errors = False
        if not all([nama_lengkap, username, no_telp, email, password, confirm_password]):
            flash('Semua field wajib diisi!', 'danger')
            errors = True
        if not re.match(r'^\d{10,13}$', no_telp):
            flash('No. telepon harus 10–13 digit angka!', 'danger')
            errors = True
        if not re.match(r'^[a-z0-9_]{3,20}$', username):
            flash('Username harus 3-20 karakter: huruf kecil, angka, underscore.', 'danger')
            errors = True
        if not re.match(r'^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$', email):
            flash('Format email tidak valid!', 'danger')
            errors = True
        if password != confirm_password:
            flash('Konfirmasi password tidak cocok!', 'danger')
            errors = True
        if len(password) < 6:
            flash('Password minimal 6 karakter!', 'danger')
            errors = True

        if errors:
            return render_template('register.html', form=request.form)

        try:
            new_user = User(
                nama_lengkap=nama_lengkap,
                username=username,
                email=email,
                no_telp=no_telp
            )
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            flash('Registrasi berhasil! Silakan login.', 'success')
            return redirect(url_for('login'))
        except IntegrityError:
            db.session.rollback()
            flash('Username atau email sudah digunakan!', 'danger')
            return render_template('register.html', form=request.form)

    return render_template('register.html', form=None)

# ===============================================================
# LOGIN
# ===============================================================
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Jika user sudah login, redirect ke halaman yang sesuai role
    if current_user.is_authenticated:
        if hasattr(current_user, 'role') and current_user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('landing'))

    if request.method == 'POST':
        identifier = request.form.get('identifier', '').strip().lower()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))

        if not identifier or not password:
            flash('Harap masukkan data dengan lengkap.', 'danger')
            return render_template('login.html', identifier=identifier)
        
        user = User.query.filter(
            db.or_(
                db.func.lower(User.username) == identifier,
                db.func.lower(User.email) == identifier
            )
        ).first()

        # Debug
        print("QUERY RESULT =>", user)
        if user:
            print("Password hash di DB:", user.password)
            print("check_password result:", user.check_password(password))
            print("Password form:", password)
        else:
            print("User tidak ditemukan")

        if user and user.check_password(password):
            login_user(user, remember=remember)
            flash('Login berhasil! Selamat datang kembali.', 'success')
            if hasattr(user, 'role') and user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('landing'))
        else:
            flash('Email/Username atau Password tidak sesuai.', 'danger')
            return render_template('login.html', identifier=identifier)

    # GET request (belum login)
    return render_template('login.html', identifier="")

# ===============================================================
# LOGOUT
# ===============================================================
@app.route('/logout')
@nocache
def logout():
    logout_user()
    session.clear()
    # UNTUK MENGHAPUS "remember" cookies SECARA PAKSA:
    resp = redirect(url_for('landing'))
    resp.set_cookie('remember_token', '', expires=0)
    flash('Anda telah Keluar.', 'info')
    return resp


# ===============================================================
# LUPA PASSWORD
# ===============================================================
@app.route('/forgot', methods=['GET', 'POST'])
def forgot():
    return render_template('forgot.html')

@app.route('/forgot_generate_link', methods=['POST'])
def forgot_generate_link():
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    no_telp = data.get('no_telp', '').strip()

    user = User.query.filter_by(email=email, no_telp=no_telp).first()
    if not user:
        return jsonify({'success': False, 'message': 'Email atau nomor telepon tidak ditemukan.'})
    reset_link = f"http://127.0.0.1:5000/reset_password/{user.id}-demoToken123"
    return jsonify({'success': True, 'reset_link': reset_link})

# ===============================================================
# RESET PASSWORD
# ===============================================================
@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        user_id, kode = token.split('-')
        user = User.query.get(int(user_id))
        if not user:
            flash('Token tidak valid.', 'danger')
            return redirect(url_for('login'))
    except Exception:
        flash('Link reset/password tidak valid.', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')
        if not password or not confirm:
            flash('Semua field wajib diisi!', 'danger')
            return render_template('reset_token.html')
        if len(password) < 6:
            flash('Password minimal 6 karakter!', 'danger')
            return render_template('reset_token.html')
        if password != confirm:
            flash('Konfirmasi password tidak cocok!', 'danger')
            return render_template('reset_token.html')
        user.set_password(password)
        db.session.commit()
        flash('Password berhasil direset! Silakan login dengan password baru.', 'success')
        return redirect(url_for('login'))

    return render_template('reset_token.html')

# ===============================================================
# PROFIL
# ===============================================================
@app.route('/profil')
@login_required
@nocache
def profil():
    return render_template('profil.html')

@app.route("/privacy")
@login_required
@nocache
def privacy():
    return render_template("privacy.html")

@app.route("/terms")
@login_required
@nocache
def terms():
    return render_template("terms.html")

@app.route('/index')
@login_required
@nocache
def index():
    user = current_user

    
    if user.role == 'admin':
        laporan_semua = Laporan.query.order_by(Laporan.id.desc()).all()
        laporan_terbaru = laporan_semua[:10]
    else:
        laporan_semua = Laporan.query.filter_by(username=user.username).order_by(Laporan.id.desc()).all()
        laporan_terbaru = laporan_semua[:10]
    
   
    total_laporan = len(laporan_semua)
    total_menunggu = len([lapor for lapor in laporan_semua if lapor.status == 'Menunggu'])
    total_diproses = len([lapor for lapor in laporan_semua if lapor.status == 'Diproses'])
    
    return render_template(
        'index.html',
        user=user,
        laporan=laporan_terbaru,
        total_laporan=total_laporan,
        total_menunggu=total_menunggu,
        total_diproses=total_diproses
    )

@app.route('/tambah-laporan')
@login_required
def tambah_laporan():
    return render_template('tambah_laporan.html')

@app.route('/laporan-saya')
@login_required
@nocache
def laporan_saya():
    return render_template('laporan_saya.html')

@app.route('/riwayat')
@login_required
@nocache
def riwayat():
    return render_template('riwayat.html')

@app.route('/dashboard/tentang')
@login_required
@nocache
def tentang():
    return render_template('tentang.html')
@app.after_request
def add_no_cache_headers(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

def nocache(view):
    @wraps(view)
    def no_cache(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    return no_cache


@app.errorhandler(403)
def forbidden(error):
    return render_template('403.html'), 403

def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not hasattr(current_user, 'role') or current_user.role != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function



@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    try:
        total_laporan = Laporan.query.count()
        total_user = User.query.count()
        total_kategori = Kategori.query.count()
        from datetime import date, timedelta
        today = date.today()
        laporan_baru = Laporan.query.filter(Laporan.tanggal >= today).count()
        user_baru = User.query.filter(User.created_at >= today - timedelta(days=7)).count()
    except Exception as e:
        print("Error dashboard admin:", e)
        flash(f"Terjadi error pada dashboard admin: {e}", "danger")
        return render_template("Admin/admin_dashboard.html", 
                              total_laporan=0, total_user=0, total_kategori=0,
                              laporan_baru=0, user_baru=0)

    return render_template(
        'Admin/admin_dashboard.html',
        total_laporan=total_laporan,
        total_user=total_user,
        total_kategori=total_kategori,
        laporan_baru=laporan_baru,
        user_baru=user_baru
    )

@app.route('/admin/laporan')
@admin_required
def admin_laporan():
    return render_template('Admin/admin_laporan.html')


@app.route('/admin/users')
@admin_required
def admin_users():
    semua_user = User.query.order_by(User.id.desc()).all()
    return render_template('Admin/admin_users.html', users=semua_user)

@app.route('/admin/kategori')
@admin_required
def admin_kategori():
    semua_kategori = Kategori.query.order_by(Kategori.id).all()
    return render_template('Admin/admin_kategori.html', kategori=semua_kategori)

@app.route('/tesforbidden')
def tesforbidden():
    abort(403)

# ===============================================================
# JALANKAN SERVER
# ===============================================================
if __name__ == '__main__':
    print("LaporIN siap dijalankan!")
    print("Login admin: username=admin, password=admin123")
    app.run(host='127.0.0.1', port=5000, debug=True)
