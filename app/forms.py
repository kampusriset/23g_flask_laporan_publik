from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, PasswordField, SelectField
from wtforms.validators import DataRequired, Length, Email

class ProfileForm(FlaskForm):
    nama_lengkap = StringField('Nama lengkap', validators=[DataRequired(), Length(max=100)])
    phone = StringField('No. Telepon', validators=[Length(max=20)])

class UserForm(FlaskForm):
    nama_lengkap = StringField('Nama lengkap', validators=[DataRequired(), Length(max=100)])
    username = StringField('Username', validators=[DataRequired(), Length(max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('No. HP')
    role = SelectField('Role', choices=[('admin', 'Admin'), ('user', 'User')], validators=[DataRequired()])
    is_active = BooleanField('Aktif?', default=True)
    password = PasswordField('Password')  # opsional saat edit
