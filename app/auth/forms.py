from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Regexp
from app.forms import ProfileForm


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit   = SubmitField('Login')
    
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
        Email(message='Format email harus valid, misal nama@mail.com.'),
        Length(max=120)
    ])

    password = PasswordField('Password', validators=[
        DataRequired(message='Password wajib diisi.'),
        Length(min=8, message='Password minimal 8 karakter.'),
        # Regexp(
        #     r'^(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).+$',
        #     message='Password harus mengandung huruf kapital, angka, dan simbol.'
        # )
    ])

    password2 = PasswordField('Ulangi Password', validators=[
        DataRequired(message='Ulangi Password wajib diisi.'),
        EqualTo('password', message='Ulangi Password harus sama persis dengan Password.')
    ])

    submit = SubmitField('Register')
