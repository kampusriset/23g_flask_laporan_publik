from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, SubmitField,
    BooleanField, SelectField
)
from wtforms.validators import DataRequired, Email, Length, EqualTo, Regexp


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit   = SubmitField("Login")
    
class ForgotPasswordForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Kirim link reset")

class ResetPasswordForm(FlaskForm):
    password = PasswordField("Password baru", validators=[DataRequired(), Length(min=8)])
    password2 = PasswordField(
        "Ulangi password baru",
        validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Ganti password")

class RegisterForm(FlaskForm):
    nama_lengkap = StringField('Nama Lengkap', validators=[
        DataRequired(message='Nama lengkap wajib diisi.'),
        Length(min=3, max=100, message='Nama 3–100 karakter.'),
        Regexp(
            r'^[A-Za-zÀ-ÿ\s]+$',
            message='Nama hanya boleh huruf dan spasi, tanpa angka/simbol.'
        )
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


class UserForm(FlaskForm):
    nama_lengkap = StringField('Nama lengkap', validators=[DataRequired(), Length(max=100)])
    username = StringField('Username', validators=[DataRequired(), Length(max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('No. HP')
    role = SelectField('Role', choices=[('admin', 'Admin'), ('user', 'User')], validators=[DataRequired()])
    is_active = BooleanField('Aktif?', default=True)
    password = PasswordField('Password')  # opsional saat edit
