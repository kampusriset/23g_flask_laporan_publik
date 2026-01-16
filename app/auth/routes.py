from flask import render_template, redirect, url_for, flash, request, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app.auth import bp
from app import db, mail # <--- PENTING: Import mail dari app
from app.models.user import User 
from app.auth.forms import LoginForm, RegisterForm, ForgotPasswordForm, ResetPasswordForm
from datetime import datetime
from flask_mail import Message # <--- PENTING: Import Message
from flask import render_template, redirect, url_for, flash, request, session, make_response
from flask_login import logout_user, login_required
# --- FUNGSI HELPER PENGIRIM EMAIL ---
def send_reset_email(user):
    token = user.get_reset_token()
    
    # Membuat pesan email
    msg = Message('Permintaan Reset Password - LaporIN',
                  sender=current_app.config['MAIL_DEFAULT_SENDER'],
                  recipients=[user.email])
    
    # _external=True PENTING agar menghasilkan URL lengkap (http://localhost:5000/...)
    url = url_for('auth.reset_password', token=token, _external=True)
    
    # Isi email (Body)
    msg.body = f'''Halo {user.nama_lengkap},

Untuk mereset password akun LaporIN Anda, silakan klik tautan berikut:
{url}

Tautan ini hanya berlaku selama 30 menit.
Jika Anda tidak merasa melakukan permintaan ini, abaikan saja email ini.

Salam,
Tim LaporIN
'''
    # Kirim email
    mail.send(msg)

# --- ROUTES ---

@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = LoginForm()

    if form.validate_on_submit():
        username = (form.username.data or "").strip()
        user = User.query.filter_by(username=username).first()

        if user and user.is_active and user.check_password(form.password.data):

            
            login_user(user, remember=False) 

            user.last_login_at = datetime.utcnow()
            db.session.commit()

            flash("Berhasil login.", "success")
            session.pop("can_access_dashboard", None)
            session.permanent = True 

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
            # Demi keamanan, sebenarnya pesan ini sebaiknya generik
            # Tapi untuk tugas kuliah, spesifik tidak apa-apa
            flash("Email tidak ditemukan dalam sistem.", "warning")
            return redirect(url_for("auth.forgot_password"))

        # --- KIRIM EMAIL ---
        try:
            send_reset_email(user)
            flash("Instruksi reset password telah dikirim ke email Anda. Silakan cek Inbox atau Spam.", "info")
            return redirect(url_for("auth.login")) # Redirect ke login, bukan langsung reset
        except Exception as e:
            # Menangkap error jika koneksi internet mati atau config salah
            print(f"Error sending email: {e}")
            flash("Terjadi kesalahan saat mengirim email. Pastikan koneksi internet lancar.", "danger")

    return render_template("pages/auth/forgot_password.html", form=form)


@bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    user = User.verify_reset_token(token)
    
    if not user:
        flash("Link reset password tidak valid atau sudah kedaluwarsa.", "danger")
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
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = RegisterForm()

    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('Username sudah dipakai, silakan gunakan yang lain.', 'danger')
            return render_template('pages/auth/register.html', form=form)

        if User.query.filter_by(email=form.email.data).first():
            flash('Email sudah terdaftar, silakan gunakan email lain.', 'danger')
            return render_template('pages/auth/register.html', form=form)

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
        
        flash('Registrasi sukses! Silakan login.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('pages/auth/register.html', form=form)

@bp.route('/change_password', methods=['POST'])
@login_required
def change_password():
    # 1. Ambil data
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')

    # 2. Validasi Password Lama
    if not current_user.check_password(current_password):
        flash('Password saat ini salah.', 'danger')
        return redirect(url_for('main.settings'))

    # 3. Validasi Password Baru
    if new_password != confirm_password:
        flash('Konfirmasi password baru tidak cocok.', 'danger')
        return redirect(url_for('main.settings'))
    
    if len(new_password) < 6:
        flash('Password baru minimal 6 karakter.', 'danger')
        return redirect(url_for('main.settings'))

    # 4. Simpan Password Baru
    current_user.set_password(new_password)
    db.session.commit()
    
    flash('Password berhasil diubah.', 'success')
    return redirect(url_for('main.settings'))


@bp.route('/logout')
@login_required
def logout():
    logout_user()

    session.clear()
    
    flash('Logout berhasil.', 'success')
    response = make_response(redirect(url_for('main.index')))
    response.set_cookie('session', '', expires=0, path='/')
    response.set_cookie('remember_token', '', expires=0, path='/')
    
    return response