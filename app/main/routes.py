from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.main import bp
from app.models import Laporan
from app.forms import ProfileForm  

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


@bp.route('/')
def index():
    return render_template('pages/main/index.html')


@bp.route('/dashboard')
@login_required
def dashboard():
    laporans = Laporan.query.filter_by(user_id=current_user.id).all()

    count_diajukan = Laporan.query.filter_by(user_id=current_user.id, status='diajukan').count()
    count_diproses = Laporan.query.filter_by(user_id=current_user.id, status='diproses').count()
    count_ditolak  = Laporan.query.filter_by(user_id=current_user.id, status='ditolak').count()
    count_selesai  = Laporan.query.filter_by(user_id=current_user.id, status='selesai').count()

    return render_template(
        'pages/main/user_dashboard.html',
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


@bp.route('/notifications')
@login_required
def notifications():
    return render_template('pages/main/notifications.html')


@bp.route('/settings')
@login_required
def settings():
    return render_template('pages/main/settings.html')
