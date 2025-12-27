from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Length

class ProfileForm(FlaskForm):
    nama_lengkap = StringField('Nama lengkap', validators=[DataRequired(), Length(max=100)])
    phone = StringField('No. Telepon', validators=[Length(max=20)])
