from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.main import bp
from app.models import Laporan
from app.forms import ProfileForm  
from flask import session 

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()

    if form.validate_on_submit():
        current_user.nama_lengkap = form.nama_lengkap.data
        current_user.phone = form.phone.data          
        db.session.commit()
        flash('Profil berhasil diperbarui.', 'success')
        return redirect(url_for('main.profile'))

    if not form.is_submitted():
        form.nama_lengkap.data = current_user.nama_lengkap
        form.phone.data = current_user.phone          

    stats = {
        "total_reports": getattr(current_user, 'total_reports', 0),
        "completed_reports": getattr(current_user, 'completed_reports', 0),
    }

    return render_template('pages/main/profile.html', form=form, stats=stats)

@bp.route("/")
def index():
    print("AUTH?", current_user.is_authenticated)
    return render_template("pages/main/index.html")

@bp.route('/dashboard')
@login_required
def dashboard():
    # Hanya boleh diakses kalau datang lewat tombol "Mulai Laporkan"
    if not session.get("can_access_dashboard"):
        flash("Silakan klik tombol 'Mulai Laporkan' untuk membuka dashboard.", "warning")
        return redirect(url_for("main.index"))

    # Kalau admin nekat buka /dashboard (punya user)
    if current_user.role == "admin":
        flash("Akses halaman tidak di izinkan!", "warning")
        return redirect(url_for("admin.dashboard"))

    # Kalau user biasa, tampilkan dashboard user
    laporans = Laporan.query.filter_by(user_id=current_user.id).all()

    count_diajukan = Laporan.query.filter_by(user_id=current_user.id, status="diajukan").count()
    count_diproses = Laporan.query.filter_by(user_id=current_user.id, status="diproses").count()
    count_ditolak  = Laporan.query.filter_by(user_id=current_user.id, status="ditolak").count()
    count_selesai  = Laporan.query.filter_by(user_id=current_user.id, status="selesai").count()

    return render_template(
        "pages/main/user_dashboard.html",
        laporans=laporans,
        count_diajukan=count_diajukan,
        count_diproses=count_diproses,
        count_ditolak=count_ditolak,
        count_selesai=count_selesai,
    )

@bp.route('/about')
@login_required
def about():
    return render_template('pages/main/about.html')

@bp.route("/after-login")
@login_required
def after_login():
    session["can_access_dashboard"] = True
    if current_user.role == "admin":
        return redirect(url_for("admin.dashboard"))
    else:
        return redirect(url_for("main.dashboard"))

@bp.route('/notifications')
@login_required
def notifications():
    notifikasi_list = Laporan.query.filter(
        Laporan.user_id == current_user.id,
        Laporan.status.in_(['diproses', 'selesai', 'ditolak'])
    ).order_by(Laporan.updated_at.desc()).all()

    return render_template('pages/main/notifications.html', notifications=notifikasi_list)



@bp.route('/settings')
@login_required
def settings():
    return render_template('pages/main/settings.html')
