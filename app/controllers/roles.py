from . import BaseViewSU, expose
from . import send_file, request, redirect, url_for 
from . import db
from . import flash

from app.models.roles import Role
from app.views.roles import RolesForm

from .table_utils import GetTableHeader, getTableRecords, initTableRecords
from .download_utils import downloadCSV

class RolesRoute(BaseViewSU):
    @expose("/", methods=["GET", "POST"])
    def index(self):
        # define initial variable
        page, per_page, table_search, search_key, _col, _type, sort_type = initTableRecords()

        # Create Table Record
        filters = ['name', 'description']
        tableRecords, min_page, max_page, count = getTableRecords(Role, search_key, filters, sort_type, _col, page, per_page)

        # Create Table Header
        col_exclude = []
        sort_exclude = ['id']
        overide_label = dict(
            id = 'No'
        )
        tableHeader = GetTableHeader(Role, col_exclude, sort_exclude, overide_label)

        # Create Header Control
        headerCtrl = dict(
            name = 'Role',
            is_search = True,
            search_act = 'roles.index',
            table_search = table_search,
            is_export = True,
            export_act = 'roles.download',
            export_filename = 'Export - Role.csv',
            sort_act = 'roles.index',
            detail_act = 'roles.detail',
            is_add_new = False
        )

        # Create Footer Control
        footerCtrl = dict(
            min_page=min_page, 
            max_page=max_page, 
            count=count,
            _type=_type,
            _col=_col,
            pagination_act = 'roles.index'
        )
        return self.render("admin/roles.html", 
                            tableRecords=tableRecords, 
                            tableHeader=tableHeader,
                            headerCtrl=headerCtrl,
                            footerCtrl=footerCtrl
                        )

    @expose("/download/<filename>")
    def download(self, filename):
        tableRecords = Role().query.all()
        col_exclude = ['id']
        csv_path = downloadCSV(Role, tableRecords, filename, col_exclude, 'static/csv-download')
        return send_file(csv_path, 
                        attachment_filename=filename, 
                        as_attachment=True, 
                        mimetype='text/csv')

    @expose("/detail/<int:_id>", methods=["GET", "POST"])
    def detail(self, _id):
        form = RolesForm()
        getRoleById = Role.query.get(_id)

        if form.validate_on_submit() and getRoleById:
            getRoleById.name = form.name.data
            getRoleById.description = form.description.data
            db.session.commit()
            flash('Role ' + getRoleById.name + ' has been updated!', 'success')
            return redirect(url_for('roles.index'))

        elif request.method == 'GET' and getRoleById:
            form.name.data = getRoleById.name
            form.description.data = getRoleById.description

        inputField = ['name', 'description']
        submitField = ['submit']
        indexField = ['id']

        formCtrl = dict(
            _id=_id,
            inputField = inputField,
            submitField = submitField,
            indexField=indexField,
            form_act = "roles.detail",
            cancel_act = "roles.index",
            form_name = 'Role Form', 
        )
        return self.render("admin/role_detail.html",
                            form=form,
                            formCtrl=formCtrl)