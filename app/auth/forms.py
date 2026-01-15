from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, SubmitField,
    BooleanField, SelectField
)
from wtforms.validators import DataRequired, Email, Length, EqualTo, Regexp

# --- Form Login ---
class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    # Tambahan optional: remember me sering dipakai di login
    remember = BooleanField('Ingat Saya') 
    submit   = SubmitField("Login")

# --- Form Lupa Password ---
class ForgotPasswordForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Kirim link reset")

# --- Form Reset Password ---
class ResetPasswordForm(FlaskForm):
    password = PasswordField(
        'Password Baru', 
        validators=[
            DataRequired(), 
            Length(min=6, message="Password minimal 6 karakter")
        ]
    )
    confirm_password = PasswordField(
        'Konfirmasi Password', 
        validators=[
            DataRequired(), 
            EqualTo('password', message='Password tidak cocok.')
        ]
    )
    submit = SubmitField('Ubah Password')

# --- Form Register ---
class RegisterForm(FlaskForm):
    nama_lengkap = StringField('Nama Lengkap', validators=[
        DataRequired(message='Nama lengkap wajib diisi.'),
        Length(min=3, max=100, message='Nama 3–100 karakter.'),
        # Regexp(
        #     r'^[A-Za-zÀ-ÿ\s]+$',
        #     message='Nama hanya boleh huruf dan spasi, tanpa angka/simbol.'
        # )
    ])

    username = StringField('Username', validators=[
        DataRequired(message='Username wajib diisi.'),
        Length(min=3, max=30, message='Username 3–30 karakter.'),
        Regexp(
            r'^\w+$',
            message='Username hanya boleh huruf, angka, dan underscore, tanpa spasi.'
        )
    ])

    email = StringField('Email', validators=[
        DataRequired(message='Email wajib diisi.'),
        Email(message='Format email harus valid.'),
        Length(max=120)
    ])

    password = PasswordField('Password', validators=[
        DataRequired(message='Password wajib diisi.'),
        Length(min=8, message='Password minimal 8 karakter.')
    ])

    password2 = PasswordField('Ulangi Password', validators=[
        DataRequired(message='Ulangi Password wajib diisi.'),
        EqualTo('password', message='Ulangi Password harus sama persis dengan Password.')
    ])

    submit = SubmitField('Register')

# --- Form Admin User Management ---
class UserForm(FlaskForm):
    nama_lengkap = StringField('Nama lengkap', validators=[DataRequired(), Length(max=100)])
    username = StringField('Username', validators=[DataRequired(), Length(max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('No. HP')
    role = SelectField('Role', choices=[('admin', 'Admin'), ('user', 'User')], validators=[DataRequired()])
    is_active = BooleanField('Aktif?', default=True)
    password = PasswordField('Password')  # opsional saat edit

# --- Form Profil Pengguna (YANG SEBELUMNYA HILANG) ---
class ProfileForm(FlaskForm):
    nama_lengkap = StringField('Nama Lengkap', validators=[
        DataRequired(),
        Length(min=3, max=100, message="Nama harus antara 3-100 karakter")
    ])
    
    phone = StringField('Nomor Telepon', validators=[
        DataRequired(),
        Length(min=10, max=15, message="Nomor telepon harus 10-15 digit"),
        Regexp(r'^[0-9]+$', message="Hanya angka yang diperbolehkan")
    ])
    
    submit = SubmitField('Simpan Perubahan')