from flask import render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from app.auth import bp
from app.models import db, User
from app.auth.forms import LoginForm, RegisterForm, ForgotPasswordForm, ResetPasswordForm
from datetime import datetime
from app.auth.forms import ForgotPasswordForm
from flask import url_for
from app.email import send_email 

@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = LoginForm()

    if form.validate_on_submit():
        username = (form.username.data or "").strip()
        user = User.query.filter_by(username=username).first()

        if user and user.is_active and user.check_password(form.password.data):
            # ambil dari field form jika ada, fallback ke request.form
            remember = getattr(form, "remember", None)
            if remember is not None:
                remember = bool(remember.data)
            else:
                remember = request.form.get("remember") in ("y", "on", "true")

            login_user(user, remember=remember)

            user.last_login_at = datetime.utcnow()
            db.session.commit()

            flash("Berhasil login.", "success")
            session.pop("can_access_dashboard", None)

            next_page = request.args.get("next")
            return redirect(next_page or url_for("main.index"))
        else:
            flash("Username, password, atau status akun tidak valid.", "danger")

    return render_template("pages/auth/login.html", form=form)

@bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = ForgotPasswordForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        user = User.query.filter_by(email=email).first()

        if not user:
            flash("Email tidak ditemukan.", "warning")
            return redirect(url_for("auth.forgot_password"))

        # Sementara: langsung arahkan ke halaman reset password
        token = user.get_reset_token()
        flash("Silakan masukkan password baru.", "info")
        return redirect(url_for("auth.reset_password", token=token))

    return render_template("pages/auth/forgot_password.html", form=form)

@bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    user = User.verify_reset_token(token)
    if not user:
        flash("Token reset password tidak valid atau sudah kedaluwarsa.", "danger")
        return redirect(url_for("auth.forgot_password"))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash("Password berhasil diubah. Silakan login dengan password baru.", "success")
        return redirect(url_for("auth.login"))

    return render_template("pages/auth/reset_password.html", form=form)


@bp.route('/register', methods=['GET', 'POST'])
def register():
    # Kalau sudah login, kirim ke index dulu
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = RegisterForm()

    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('Username sudah dipakai, silakan gunakan yang lain.')
            return redirect(url_for('auth.register'))

        if User.query.filter_by(email=form.email.data).first():
            flash('Email sudah terdaftar, silakan gunakan email lain.')
            return redirect(url_for('auth.register'))

        user = User(
            nama_lengkap=form.nama_lengkap.data,
            username=form.username.data,
            email=form.email.data,
            role='pengunjung',
            phone='-'
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registrasi sukses! Silakan login.')
        return redirect(url_for('auth.login'))

    # SETIAP GET / REFRESH: form baru, kosong, tanpa error
    form = RegisterForm(formdata=None)

    return render_template('pages/auth/register.html', form=form)


@bp.route('/logout')
@login_required
def logout():
    logout_user()         
    session.clear()
    flash('Logout berhasil. Silakan login kembali untuk melanjutkan.', 'success')
    response = redirect(url_for('main.index'))
    response.delete_cookie('session')
    response.delete_cookie('remember_token') 
    return response



