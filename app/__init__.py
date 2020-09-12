import os 
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from flask import Flask, url_for, render_template, request, flash, send_file, redirect
from flask_security import Security, SQLAlchemyUserDatastore
from flask_security import UserMixin, RoleMixin, current_user 
from flask_security.utils import encrypt_password
from flask_admin import Admin
from flask_admin import helpers as admin_helpers
from flask_admin import BaseView, AdminIndexView, expose
from flask_admin.contrib import sqla

app = Flask(__name__)
app.config.from_pyfile('config.py')

db = SQLAlchemy()
db.init_app(app)
db.app = app

from app.views.home import MyHomeView

from app.models.users import User 
from app.models.roles import Role

from app.controllers.users import UsersRoute
from app.controllers.roles import RolesRoute
from app.controllers.users import Profile

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

admin = Admin(
    app,
    'Arrhytmia',
    base_template='common/_layout.html',
    template_mode='bootstrap3',
    index_view=MyHomeView(),
    category_icon_classes={
        'Home': 'glyphicon glyphicon-home',
    }
)

# Add model views
admin.add_view(RolesRoute(name="Roles", menu_icon_type='fa', menu_icon_value='fa-server', endpoint="roles"))
admin.add_view(UsersRoute(name="Users", menu_icon_type='fa', menu_icon_value='fa-users', endpoint='users'))
admin.add_view(Profile(name="Profile", endpoint='profile'))

# define a context processor for merging flask-admin's template context into the
# flask-security views.
@security.context_processor
def security_context_processor():
    return dict(
        admin_base_template=admin.base_template,
        admin_view=admin.index_view,
        h=admin_helpers,
        get_url=url_for
    )

# @app.cli.command()
def build_sample_db():
    """
    Populate a small db with some example entries.
    """
    import string
    import random

    db.drop_all()
    db.create_all()

    with app.app_context():
        user_role = Role(name='user')
        super_user_role = Role(name='superuser')
        db.session.add(user_role)
        db.session.add(super_user_role)
        db.session.commit()

        test_user = user_datastore.create_user(
            first_name='Admin',
            email='admin',
            password=encrypt_password('admin'),
            roles=[user_role, super_user_role]
        )

        db.session.commit()
    return

# Flask views
@app.route('/')
def index():
    return render_template('index.html')


