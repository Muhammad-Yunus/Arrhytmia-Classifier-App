from . import BaseViewSU, expose
from . import send_file, request, redirect, url_for 
from . import db, current_user
from . import flash
from . import secure_filename
from . import os
from . import ast
from . import json 

from app.models.ecgs import Ecg
from app.views.ecgs import EcgsForm

from .table_utils import GetTableHeader, getTableRecords, initTableRecords
from .download_utils import downloadCSV, getFullPath


import requests

def save_ecg_csv(file_ecg):
        print(dir(file_ecg.name))
        csv_fn = secure_filename(file_ecg.filename)
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
        col_exclude = ['file_type', 'procced_name']
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
            delete_act = "ecgs.delete",
            detail_act = 'ecgs.detail',
            procced_act = 'ecgs.proccess',
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

    @expose("/proccess/<int:_id>")
    def proccess(self, _id):
        getEcgById = Ecg.query.get(_id)
        if getEcgById.is_procced :
            flash('File ECG %s, sudah di prosess!' % getEcgById.file_name, 'success')
        else :
            try :
                url = "http://127.0.0.1:5001/ecg_split_sequence"
                dict_response = requests.get(url, params={
                                                    'filename': getEcgById.file_name,
                                                    'fs' : getEcgById.fs
                                                    }).content
                dict_response = json.loads(dict_response)
                print("[INFO] API result : ", dict_response)
                if dict_response['status'] :
                    getEcgById.procced_name = dict_response['filename']
                    getEcgById.is_procced = True
                    db.session.commit()
                    flash('File ECG %s, berhasil di prosess!' % getEcgById.file_name, 'success')
                else :
                    flash('File ECG %s, gagal di prosess!' % getEcgById.file_name, 'error')
            except Exception as e:
                flash('Gagal terhubung ke API "ecg_split_sequence/"!', 'error')
                print("\x1b[0;31;40m [ERROR] ", e, "\x1b[0m\n\n")
        return redirect(url_for('ecgs.index'))

    @expose("/detail/<int:_id>", methods=["GET", "POST"])
    def detail(self, _id):
        form = EcgsForm()
        getEcgById = Ecg.query.get(_id)

        ecg_name = 'ecg_data.csv' # default ecg filename

        # Update record
        if form.validate_on_submit() and getEcgById:
            file_ecg = form.file_ecg.data
            ecg_file_name = save_ecg_csv(file_ecg)
            ecg_name = ecg_file_name
            getEcgById.name = form.name.data
            getEcgById.file_name = ecg_file_name
            getEcgById.fs = int(form.fs.data)
            getEcgById.upload_by = current_user.id
            db.session.commit()
            flash('Data ECG ' + getEcgById.name + ' has been uploaded!', 'success')
            return redirect(url_for('ecgs.index'))
        
        # Add new record
        if form.validate_on_submit():
            file_ecg = form.file_ecg.data
            ecg_file_name = save_ecg_csv(file_ecg)
            ecg_name = ecg_file_name
            ecg = Ecg(
                name = form.name.data,
                file_name = ecg_file_name,
                fs = int(form.fs.data),
                upload_by = current_user.first_name
            )
            db.session.add(ecg)
            db.session.commit()
            flash('Data ECG ' + ecg.name + ' has been uploaded!', 'success')
            return redirect(url_for('ecgs.index'))

        elif request.method == 'GET' and getEcgById:
            form.name.data = getEcgById.name
            ecg_name = getEcgById.file_name

        inputField = ['name', 'fs', 'file_ecg']
        submitField = ['submit']
        indexField = ['id']

        formCtrl = dict(
            _id=_id,
            inputField = inputField,
            submitField = submitField,
            indexField=indexField,
            form_act = "ecgs.detail",
            cancel_act = "ecgs.index",
            download_act = "ecgs.model_download",
            download_name = ecg_name,
            delete_act = "ecgs.delete",
            form_name = 'ECG Data Form', 
            is_multipart = True
        )
        return self.render("admin/ecg_detail.html",
                            form=form,
                            formCtrl=formCtrl)

    @expose("/ecg/download/<filename>")
    def model_download(self, filename):
        model_path = getFullPath(filename, 'static/csv-upload')
        return send_file(model_path, 
                        attachment_filename=filename, 
                        as_attachment=True, 
                        mimetype='application/octet-stream')

    @expose("/delete/<int:_id>")
    def delete(self, _id):
        getEcgById = Ecg.query.get(_id)
        db.session.delete(getEcgById)
        db.session.commit()
        flash('Ecg file ' + getEcgById.name + ' has been deleted!', 'success')
        return redirect(url_for('ecgs.index'))