from . import FlaskForm
from . import datetime

from . import StringField, SubmitField, BooleanField, FileField
from . import DataRequired, Length, ValidationError

from app.models.ecgs import Ecg

class EcgsForm(FlaskForm):
    name = StringField('Name',
                           validators=[DataRequired(), Length(min=2, max=20)])
    file_ecg = FileField('Data ECG (CSV)',
                           validators=[DataRequired()])
    submit = SubmitField('Upload')

    def validate_name(self, name):
        ecg = Ecg.query.filter_by(name=name.data).first()
        if ecg and name.data == ecg.name:
            raise ValidationError('That name is taken. Please choose a different one.')