from . import BaseViewSU, expose
from . import send_file, request, redirect, url_for 
from . import db, current_user
from . import flash
from . import secure_filename
from . import os

from app.models.ecgs import Ecg
from app.views.ecgs import EcgsForm

from .table_utils import GetTableHeader, getTableRecords, initTableRecords
from .download_utils import downloadCSV

def save_ecg_csv(file_ecg):
        csv_fn = secure_filename(file_ecg)
        root_path = os.path.dirname(os.path.dirname(__file__))
        image_path = os.path.join(root_path, 'static/csv-upload', csv_fn)

        file_ecg.save(image_path)
        return csv_fn

class EcgRoute(BaseViewSU):
    @expose("/", methods=["GET", "POST"])
    def index(self):
        # define initial variable
        page, per_page, table_search, search_key, _col, _type, sort_type = initTableRecords()

        # Create Table Record
        filters = ['name', 'file_name']
        tableRecords, min_page, max_page, count = getTableRecords(Ecg, search_key, filters, sort_type, _col, page, per_page)

        # Create Table Header
        col_exclude = ['file_type']
        sort_exclude = ['id', 'is_procced']
        overide_label = dict(
            id = 'No'
        )
        tableHeader = GetTableHeader(Ecg, col_exclude, sort_exclude, overide_label)

        # Create Header Control
        headerCtrl = dict(
            name = 'Ecg',
            is_search = True,
            search_act = 'ecgs.index',
            table_search = table_search,
            is_export = True,
            export_act = 'ecgs.download',
            export_filename = 'Export - Role.csv',
            sort_act = 'ecgs.index',
            detail_act = 'ecgs.detail',
            is_add_new = True
        )

        # Create Footer Control
        footerCtrl = dict(
            min_page=min_page, 
            max_page=max_page, 
            count=count,
            _type=_type,
            _col=_col,
            pagination_act = 'ecgs.index'
        )
        return self.render("admin/ecgs.html", 
                            tableRecords=tableRecords, 
                            tableHeader=tableHeader,
                            headerCtrl=headerCtrl,
                            footerCtrl=footerCtrl
                        )

    @expose("/download/<filename>")
    def download(self, filename):
        tableRecords = Ecg().query.all()
        col_exclude = ['id']
        csv_path = downloadCSV(Ecg, tableRecords, filename, col_exclude, 'static/csv-download')
        return send_file(csv_path, 
                        attachment_filename=filename, 
                        as_attachment=True, 
                        mimetype='text/csv')

    @expose("/detail/<int:_id>", methods=["GET", "POST"])
    def detail(self, _id):
        form = EcgsForm()
        getEcgById = Ecg.query.get(_id)

        # Update record
        if form.validate_on_submit() and getEcgById:
            file_ecg = form.file_ecg.data
            ecg_file_name = save_ecg_csv(file_ecg)
            getEcgById.name = form.name.data
            getEcgById.file_name = ecg_file_name
            getEcgById.upload_by = current_user.id
            db.session.commit()
            flash('Data ECG ' + getEcgById.name + ' has been uploaded!', 'success')
            return redirect(url_for('ecgs.index'))
        
        # Add new record
        if form.validate_on_submit():
            file_ecg = form.file_ecg.data
            ecg_file_name = save_ecg_csv(file_ecg)
            ecg = Ecg(
                name = form.name.data,
                file_name = ecg_file_name,
                upload_by = current_user.id
            )
            db.session.add(ecg)
            db.session.commit()
            flash('Data ECG ' + ecg.name + ' has been uploaded!', 'success')
            return redirect(url_for('ecgs.index'))

        elif request.method == 'GET' and getEcgById:
            form.name.data = getEcgById.name

        inputField = ['name', 'file_ecg']
        submitField = ['submit']
        indexField = ['id']

        formCtrl = dict(
            _id=_id,
            inputField = inputField,
            submitField = submitField,
            indexField=indexField,
            form_act = "ecgs.detail",
            cancel_act = "ecgs.index",
            is_multipart = True
        )
        return self.render("admin/ecg_detail.html",
                            form=form,
                            formCtrl=formCtrl)