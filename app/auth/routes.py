from flask import render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from app.auth import bp
from app.models import db, User
from app.auth.forms import LoginForm, RegisterForm
from datetime import datetime


@bp.route('/login', methods=['GET', 'POST'])
def login():
    # Kalau sudah login, selalu ke index dulu
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user and user.check_password(form.password.data):
            remember = request.form.get('remember') == 'y'
            login_user(user, remember=remember)

            user.last_login_at = datetime.utcnow()
            db.session.commit()

            flash('Berhasil login.', 'success')
            # reset tiket dashboard
            session.pop("can_access_dashboard", None)

            # SELALU ke index, tidak pakai next lagi
            return redirect(url_for('main.index'))
        else:
            flash('Username atau password salah.', 'danger')

    # GET pertama kali atau form tidak valid
    return render_template('pages/auth/login.html', form=form)


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
    return redirect(url_for('main.index'))

