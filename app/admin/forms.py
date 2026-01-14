from flask_wtf import FlaskForm
from wtforms import SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional

class ReportStatusForm(FlaskForm):
    status = SelectField(
        "Status",
        choices=[
            ("diajukan", "Diajukan"),
            ("diproses", "Diproses"),
            ("selesai", "Selesai"),
            ("ditolak", "Ditolak"),
        ],
        validators=[DataRequired()],
    )
    ringkasan_hasil = TextAreaField("Ringkasan hasil", validators=[Optional()])
    alasan_ditolak = TextAreaField("Alasan penolakan", validators=[Optional()])
    submit = SubmitField("Update")
