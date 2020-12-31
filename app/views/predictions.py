from . import FlaskForm
from . import encrypt_password
from . import datetime

from . import StringField, FloatField

from app.models.predictions import Prediction


class PredictionsForm(FlaskForm):
    label = StringField('Label')
    confidence = FloatField('Confidence')

