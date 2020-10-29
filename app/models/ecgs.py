from . import db
from . import UserMixin
from . import datetime

class Ecg(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(20), nullable=False, default='csv')
    is_procced = db.Column(db.Boolean())
    upload_at = db.Column(db.DateTime(), default=datetime.now)
    upload_by = db.Column(db.Integer)

    def __str__(self):
        return self.name