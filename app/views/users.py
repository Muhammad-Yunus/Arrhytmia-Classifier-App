from . import FlaskForm
from . import encrypt_password
from . import datetime

from . import StringField, SubmitField, BooleanField, SelectMultipleField
from . import DataRequired, Length, Email

from app.models.users import User
from app.models.roles import Role


class UsersForm(FlaskForm):
    first_name = StringField('First Name',
                           validators=[DataRequired(), Length(min=2, max=20)])
    last_name = StringField('Last Name')
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    role = SelectMultipleField('Role', choices = [(form.name, form.name) for form in Role.query.all()])
    active = BooleanField('Active')
    submit = SubmitField('Update')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user and email.data != user.email:
            raise ValidationError('That email is taken. Please choose a different one.')

