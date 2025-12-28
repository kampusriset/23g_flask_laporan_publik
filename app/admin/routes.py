from functools import wraps

from flask import abort, render_template
from flask_login import current_user, login_required
from app import db
from app.admin import bp
from app.models import User, Laporan
from sqlalchemy import select

def admin_required(view):
    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if getattr(current_user, "role", None) != "admin":
            abort(403)
        return view(*args, **kwargs)
    return wrapped


@bp.route("/dashboard")
@admin_required
def dashboard():
    total_users = User.query.count()
    total_reports = Laporan.query.count()
    reports_in_progress = Laporan.query.filter_by(status="diproses").count()
    reports_done = Laporan.query.filter_by(status="selesai").count()
    latest_reports = (
        Laporan.query.order_by(Laporan.created_at.desc())
        .limit(10)
        .all()
    )
    return render_template(
        "admin/admin_dashboard.html",
        total_users=total_users,
        total_reports=total_reports,
        reports_in_progress=reports_in_progress,
        reports_done=reports_done,
        latest_reports=latest_reports,
    )
@bp.route('/users')
@login_required
@admin_required
def user_list():
    # Menggunakan syntax SQLAlchemy 2.0 style (db.select)
    stmt = select(User).order_by(User.created_at.desc())
    users = db.session.execute(stmt).scalars().all()
    return render_template('admin/user_list.html', users=users)

# --- CREATE: Tambah User Baru ---
@bp.route('/users/new', methods=['GET', 'POST'])
@login_required
@admin_required
def user_create():
    form = UserForm()
    
    if form.validate_on_submit():
        # Cek apakah username/email sudah ada
        stmt = select(User).where((User.username == form.username.data) | (User.email == form.email.data))
        existing_user = db.session.execute(stmt).scalars().first()
        
        if existing_user:
            flash('Username atau Email sudah terdaftar.', 'danger')
        else:
            # Buat object user baru
            new_user = User(
                nama_lengkap=form.nama_lengkap.data,
                username=form.username.data,
                email=form.email.data,
                phone=form.phone.data,
                role=form.role.data,
                is_active=form.is_active.data
            )
            # Set password menggunakan method di Model
            if form.password.data:
                new_user.set_password(form.password.data)
            else:
                # Default password jika admin lupa isi (opsional)
                new_user.set_password('12345678') 
            
            db.session.add(new_user)
            db.session.commit()
            flash('User berhasil ditambahkan.', 'success')
            return redirect(url_for('admin.user_list'))
            
    return render_template('admin/user_form.html', form=form, title="Tambah User")

# --- UPDATE: Edit User ---
@bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def user_edit(user_id):
    # Fetch user by ID
    user = db.session.get(User, user_id)
    if not user:
        flash('User tidak ditemukan', 'danger')
        return redirect(url_for('admin.user_list'))

    form = UserForm(obj=user) # Isi form dengan data user saat ini

    if form.validate_on_submit():
        # Cek duplikasi username/email (kecuali milik user itu sendiri)
        stmt = select(User).where(
            ((User.username == form.username.data) | (User.email == form.email.data)) & 
            (User.id != user_id)
        )
        duplicate = db.session.execute(stmt).scalars().first()

        if duplicate:
            flash('Username atau Email sudah digunakan user lain.', 'danger')
        else:
            # Update data
            user.nama_lengkap = form.nama_lengkap.data
            user.username = form.username.data
            user.email = form.email.data
            user.phone = form.phone.data
            user.role = form.role.data
            user.is_active = form.is_active.data

            # Update password HANYA jika form diisi
            if form.password.data:
                user.set_password(form.password.data)
            
            db.session.commit()
            flash('Data user berhasil diperbarui.', 'success')
            return redirect(url_for('admin.user_list'))

    return render_template('admin/user_form.html', form=form, title="Edit User", user=user)

# --- DELETE: Hapus User ---
@bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def user_delete(user_id):
    user = db.session.get(User, user_id)
    
    if user:
        if user.id == current_user.id:
            flash('Anda tidak bisa menghapus akun sendiri saat sedang login.', 'warning')
        else:
            db.session.delete(user)
            db.session.commit()
            flash('User berhasil dihapus.', 'success')
    else:
        flash('User tidak ditemukan.', 'danger')
        
    return redirect(url_for('admin.user_list'))