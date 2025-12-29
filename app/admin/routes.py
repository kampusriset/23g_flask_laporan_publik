from functools import wraps

from flask import (
    abort, render_template, request, redirect, url_for, flash
)
from flask_login import current_user, login_required
from sqlalchemy import select, or_

from app import db
from app.admin import bp
from app.models import User, Laporan
from app.forms import UserForm


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
    # hanya hitung laporan dari user non-admin
    base_reports = (
        Laporan.query
        .join(User)
        .filter(User.role != "admin")
    )

    total_users = User.query.count()
    total_reports = base_reports.count()
    reports_in_progress = base_reports.filter(Laporan.status == "diproses").count()
    reports_done = base_reports.filter(Laporan.status == "selesai").count()
    latest_reports = (
        base_reports
        .order_by(Laporan.created_at.desc())
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


# ---------- KELOLA USER ----------

@bp.route("/users")
@admin_required
def user_list():
    stmt = select(User).order_by(User.created_at.desc())
    users = db.session.execute(stmt).scalars().all()
    return render_template("admin/user_list.html", users=users)


@bp.route("/users/new", methods=["GET", "POST"])
@admin_required
def user_create():
    form = UserForm()

    if form.validate_on_submit():
        stmt = select(User).where(
            (User.username == form.username.data) |
            (User.email == form.email.data)
        )
        existing_user = db.session.execute(stmt).scalars().first()

        if existing_user:
            flash("Username atau Email sudah terdaftar.", "danger")
        else:
            new_user = User(
                nama_lengkap=form.nama_lengkap.data,
                username=form.username.data,
                email=form.email.data,
                phone=form.phone.data,
                role=form.role.data,
                is_active=form.is_active.data,
            )
            if form.password.data:
                new_user.set_password(form.password.data)
            else:
                new_user.set_password("12345678")

            db.session.add(new_user)
            db.session.commit()
            flash("User berhasil ditambahkan.", "success")
            return redirect(url_for("admin.user_list"))

    return render_template("admin/user_form.html", form=form, title="Tambah User")


@bp.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
@admin_required
def user_edit(user_id):
    user = db.session.get(User, user_id)
    if not user:
        flash("User tidak ditemukan", "danger")
        return redirect(url_for("admin.user_list"))

    form = UserForm(obj=user)

    if form.validate_on_submit():
        stmt = select(User).where(
            ((User.username == form.username.data) |
             (User.email == form.email.data)) &
            (User.id != user_id)
        )
        duplicate = db.session.execute(stmt).scalars().first()

        if duplicate:
            flash("Username atau Email sudah digunakan user lain.", "danger")
        else:
            user.nama_lengkap = form.nama_lengkap.data
            user.username = form.username.data
            user.email = form.email.data
            user.phone = form.phone.data
            user.role = form.role.data
            user.is_active = form.is_active.data

            if form.password.data:
                user.set_password(form.password.data)

            db.session.commit()
            flash("Data user berhasil diperbarui.", "success")
            return redirect(url_for("admin.user_list"))

    return render_template(
        "admin/user_form.html",
        form=form,
        title="Edit User",
        user=user,
    )


@bp.route("/users/<int:user_id>/delete", methods=["POST"])
@admin_required
def user_delete(user_id):
    user = db.session.get(User, user_id)

    if user:
        if user.id == current_user.id:
            flash(
                "Anda tidak bisa menghapus akun sendiri saat sedang login.",
                "warning",
            )
        else:
            db.session.delete(user)
            db.session.commit()
            flash("User berhasil dihapus.", "success")
    else:
        flash("User tidak ditemukan.", "danger")

    return redirect(url_for("admin.user_list"))


# ---------- KELOLA LAPORAN ----------

@bp.route("/laporan", methods=["GET"])
@admin_required
def manage_reports():
    status = request.args.get("status", "").strip()
    q = request.args.get("q", "").strip()

    # hanya laporan dari user non-admin
    query = (
        Laporan.query
        .join(User)
        .filter(User.role != "admin")
    )

    if status:
        query = query.filter(Laporan.status == status)

    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(
                Laporan.kode_pelaporan.ilike(like),
                Laporan.judul.ilike(like),
            )
        )

    reports = query.order_by(Laporan.created_at.desc()).all()

    return render_template(
        "admin/admin_kelola_laporan.html",
        reports=reports,
        status=status,
        q=q,
    )


@bp.route("/laporan/<int:laporan_id>/status", methods=["POST"])
@admin_required
def update_report_status(laporan_id):
    new_status = request.form.get("status", "").strip()
    laporan = db.session.get(Laporan, laporan_id)

    if not laporan:
        flash("Laporan tidak ditemukan.", "danger")
        return redirect(url_for("admin.manage_reports"))

    if new_status not in ["diajukan", "diproses", "selesai", "ditolak"]:
        flash("Status tidak valid.", "danger")
        return redirect(url_for("admin.manage_reports"))

    from datetime import datetime

    laporan.status = new_status
    laporan.updated_at = datetime.utcnow()

    db.session.commit()
    flash("Status laporan berhasil diperbarui.", "success")
    return redirect(url_for("admin.manage_reports"))
