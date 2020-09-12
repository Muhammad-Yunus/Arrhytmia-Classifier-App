from . import FlaskForm

from . import StringField, TextAreaField, SubmitField
from . import DataRequired, Length

from app.models.roles import Role


class RolesForm(FlaskForm):
    name = StringField('Name',
                           validators=[DataRequired(), Length(max=80)])
    description = TextAreaField('Description')
    submit = SubmitField('Update')

    def validate_name(self, name):
        role = Role.query.filter_by(name=name.data).first()
        if role and name.data != role.name:
            raise ValidationError('That role is already created!')
