from flask import render_template, redirect, url_for, flash, session, request
from flask_login import login_required, current_user
from app import db
from app.main import bp
from app.models.laporan import Laporan 
from app.auth.forms import ProfileForm 

@bp.route("/")
def index():
    # 1. Ambil jumlah seluruh laporan
    total_laporan = Laporan.query.count()

    # 2. Ambil jumlah laporan selesai
    laporan_selesai = Laporan.query.filter_by(status='selesai').count()

    # 3. Hitung persentase
    if total_laporan > 0:
        persen_selesai = int((laporan_selesai / total_laporan) * 100)
    else:
        persen_selesai = 0

    return render_template(
        "pages/main/index.html", 
        total_laporan=total_laporan,
        persen_selesai=persen_selesai
    )

@bp.route("/after-login")
@login_required
def after_login():
    # Set session barrier agar bisa buka dashboard
    session["can_access_dashboard"] = True
    
    if current_user.role == "admin":
        return redirect(url_for("admin.dashboard"))
    else:
        return redirect(url_for("main.dashboard"))

@bp.route('/dashboard')
@login_required
def dashboard():
    # 1. Cek Session Barrier
    if not session.get("can_access_dashboard"):
        flash("Silakan klik tombol 'Mulai Laporkan' di halaman depan untuk membuka dashboard.", "warning")
        return redirect(url_for("main.index"))

    # 2. Cek Role (Admin dilarang masuk sini)
    if current_user.role == "admin":
        flash("Halaman ini khusus untuk Pengguna.", "warning")
        return redirect(url_for("admin.dashboard"))

    # 3. Ambil Data Laporan User Ini
    laporans = Laporan.query.filter_by(user_id=current_user.id).order_by(Laporan.created_at.desc()).all()

    # 4. OPTIMASI: Hitung status menggunakan Python (lebih cepat daripada query berulang)
    count_diajukan = sum(1 for l in laporans if l.status == 'diajukan')
    count_diproses = sum(1 for l in laporans if l.status == 'diproses')
    count_ditolak  = sum(1 for l in laporans if l.status == 'ditolak')
    count_selesai  = sum(1 for l in laporans if l.status == 'selesai')

    return render_template(
        "pages/main/user_dashboard.html",
        laporans=laporans,
        count_diajukan=count_diajukan,
        count_diproses=count_diproses,
        count_ditolak=count_ditolak,
        count_selesai=count_selesai,
    )

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()

    if form.validate_on_submit():
        # Update data user
        current_user.nama_lengkap = form.nama_lengkap.data
        current_user.phone = form.phone.data          
        
        db.session.commit()
        flash('Profil berhasil diperbarui.', 'success')
        return redirect(url_for('main.profile'))

    # Pre-populate form dengan data lama saat method GET
    if request.method == 'GET':
        form.nama_lengkap.data = current_user.nama_lengkap
        form.phone.data = current_user.phone          

    # Hitung Statistik User (Real-time dari Database)
    total_reports = Laporan.query.filter_by(user_id=current_user.id).count()
    completed_reports = Laporan.query.filter_by(user_id=current_user.id, status='selesai').count()

    stats = {
        "total_reports": total_reports,
        "completed_reports": completed_reports,
    }

    return render_template('pages/main/profile.html', form=form, stats=stats)

@bp.route('/about')
def about():
    return render_template('pages/main/about.html')

@bp.route('/notifications')
@login_required
def notifications():
    return render_template('pages/main/notifications.html')

@bp.route('/settings')
@login_required
def settings():
    return render_template('pages/main/settings.html')