from . import db
from . import roles_users
from . import UserMixin
from . import datetime

class Prediction(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(255), nullable=False)
    confidence = db.Column(db.Float(precision='3,2'), nullable=False)
    data = db.Column(db.String(2000), nullable=False)
    raw = db.Column(db.String(1000), nullable=False)
    create_at = db.Column(db.DateTime(), default=datetime.now)
    create_by = db.Column(db.Integer)

    def __str__(self):
        return self.email