from . import send_file, request, redirect, url_for
from . import BaseView, BaseViewSU, expose
from . import db, current_user
from . import flash
from . import os

from app.models.users import User
from app.models.roles import Role
from app.views.users import UsersForm

from .table_utils import GetTableHeader, getTableRecords, initTableRecords
from .download_utils import downloadCSV

def userDetail(self, _id, screen_act):
    form = UsersForm()
    getUserById = User.query.get(_id)

    if form.validate_on_submit() and getUserById:
        getUserById.first_name = form.first_name.data
        getUserById.last_name = form.last_name.data
        getUserById.email = form.email.data
        getUserById.active = form.active.data
        getUserById.roles = [ Role.query.filter(Role.name == role_name).first() for role_name in request.form.getlist('role')]
        db.session.commit()
        flash('User ' + getUserById.first_name + ' has been updated!', 'success')
        return redirect(url_for('users.index'))

    elif request.method == 'GET' and getUserById:
        form.first_name.data = getUserById.first_name
        form.last_name.data = getUserById.last_name
        form.email.data = getUserById.email
        form.active.data = getUserById.active
        form.role.data = getUserById.roles

    inputField = ['first_name', 'last_name', 'email', 'role', 'active']
    submitField = ['submit']
    indexField = ['id']

    formCtrl = dict(
        _id=_id,
        inputField = inputField,
        submitField = submitField,
        indexField=indexField,
        form_act = screen_act,
        cancel_act = "users.index",
    )
    return self.render("admin/user_detail.html",
                        form=form,
                        formCtrl=formCtrl)


class UsersRoute(BaseViewSU):
    @expose("/", methods=["GET", "POST"])
    def index(self):

        # define initial variable
        page, per_page, table_search, search_key, _col, _type, sort_type = initTableRecords()


        # Create Table Record
        filters = ['first_name', 'last_name', 'email']
        tableRecords, min_page, max_page, count = getTableRecords(User, search_key, filters, sort_type, _col, page, per_page)

        # Create Table Header
        col_exclude = ['password', 'roles']
        sort_exclude = ['id', 'active']
        overide_label = dict(
            id = 'No'
        )
        tableHeader = GetTableHeader(User, col_exclude, sort_exclude, overide_label)

        # Create Header Control
        headerCtrl = dict(
            name = 'User',
            is_search = True,
            search_act = 'users.index',
            table_search = table_search,
            is_export = True,
            export_act = 'users.download',
            export_filename = 'Export - User.csv',
            sort_act = 'users.index',
            detail_act = 'users.detail',
            is_add_new = False
        )

        # Create Footer Control
        footerCtrl = dict(
            min_page=min_page, 
            max_page=max_page, 
            count=count,
            _type=_type,
            _col=_col,
            pagination_act = 'users.index'
        )

        return self.render('admin/users.html', 
                            tableRecords=tableRecords, 
                            tableHeader=tableHeader,
                            headerCtrl=headerCtrl,
                            footerCtrl=footerCtrl
                        )

    @expose("/download/<filename>")
    def download(self, filename):
        tableRecords = User().query.all()
        col_exclude = ['id', 'password', 'roles']
        csv_path = downloadCSV(User, tableRecords, filename, col_exclude, 'static/csv-download')
        return send_file(csv_path, 
                        attachment_filename=filename, 
                        as_attachment=True, 
                        mimetype='text/csv')

    @expose("/detail/<int:_id>", methods=['GET', 'POST'])
    def detail(self, _id):
        return userDetail(self, _id, 'users.detail')



class Profile(BaseView):
    def is_visible(self):
        return False

    @expose("/", methods=['GET','POST'])
    def index(self):
        _id = current_user.id
        return userDetail(self, _id, 'profile.index')

