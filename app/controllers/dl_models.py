from . import BaseViewSU, expose
from . import send_file, request, redirect, url_for 
from . import db, current_user
from . import flash
from . import os

from app.models.dl_models import DL_Model
from app.views.dl_models import DLModelsForm

from .table_utils import GetTableHeader, getTableRecords, initTableRecords
from .download_utils import getFullPath


def save_model_h5(file_model, name):
        model_fn = name.lower().replace(" ", "_")
        root_path = os.path.dirname(os.path.dirname(__file__))
        full_path = os.path.join(root_path, 'static/model-upload', model_fn)

        file_model.save(full_path)
        return model_fn

class DLModelRoute(BaseViewSU):
    @expose("/", methods=["GET", "POST"])
    def index(self):
        # define initial variable
        page, per_page, table_search, search_key, _col, _type, sort_type = initTableRecords()

        # Create Table Record
        filters = ['name', 'file_name']
        tableRecords, min_page, max_page, count = getTableRecords(DL_Model, search_key, filters, sort_type, _col, page, per_page)

        # Create Table Header
        col_exclude = ['file_type']
        sort_exclude = ['id', 'is_used']
        overide_label = dict(
            id = 'No'
        )
        tableHeader = GetTableHeader(DL_Model, col_exclude, sort_exclude, overide_label)

        # Create Header Control
        headerCtrl = dict(
            name = 'Model',
            is_search = True,
            search_act = 'models.index',
            table_search = table_search,
            is_export = True,
            export_act = 'models.download',
            export_filename = 'Export - Model.h5',
            sort_act = 'models.index',
            delete_act = "models.delete",
            detail_act = 'models.detail',
            is_add_new = True
        )

        # Create Footer Control
        footerCtrl = dict(
            min_page=min_page, 
            max_page=max_page, 
            count=count,
            _type=_type,
            _col=_col,
            pagination_act = 'models.index'
        )
        return self.render("admin/models.html", 
                            tableRecords=tableRecords, 
                            tableHeader=tableHeader,
                            headerCtrl=headerCtrl,
                            footerCtrl=footerCtrl
                        )

    @expose("/download/<filename>")
    def download(self, filename):
        model_path = getFullPath(filename, 'static/csv-download')
        return send_file(model_path, 
                        attachment_filename=filename, 
                        as_attachment=True, 
                        mimetype='application/octet-stream')

    @expose("/detail/<int:_id>", methods=["GET", "POST"])
    def detail(self, _id):
        form = DLModelsForm()
        getDLModelById = DL_Model.query.get(_id)
        
        model_name = 'model.h5' # default model name

        # Update record
        if form.is_submitted() and getDLModelById:
            if form.file_model.data.filename != "" :
                file_model = form.file_model.data
                model_file_name = save_model_h5(file_model, form.name.data + ".h5")
                model_name = model_file_name
                getDLModelById.file_name = model_file_name
            getDLModelById.name = form.name.data
            getDLModelById.upload_by = current_user.first_name
            getDLModelById.is_used = form.is_used.data
            db.session.commit()
            flash('Model ' + getDLModelById.name + ' has been uploaded!', 'success')
            return redirect(url_for('models.index'))
        
        # Add new record
        if form.is_submitted() and form.validate_on_submit():
            file_model = form.file_model.data
            model_file_name = save_model_h5(file_model, form.name.data + ".h5")
            model_name = model_file_name
            dl_model = DL_Model(
                name = form.name.data,
                file_name = model_file_name,
                upload_by = current_user.first_name,
                is_used = form.is_used.data
            )
            db.session.add(dl_model)
            db.session.commit()
            flash('Model ' + dl_model.name + ' has been uploaded!', 'success')
            return redirect(url_for('models.index'))

        elif request.method == 'GET' and getDLModelById:
            form.name.data = getDLModelById.name
            form.is_used.data = getDLModelById.is_used
            model_name = getDLModelById.file_name

        inputField = ['name', 'is_used', 'file_model']
        submitField = ['submit']
        indexField = ['id']

        formCtrl = dict(
            _id=_id,
            inputField = inputField,
            submitField = submitField,
            indexField=indexField,
            form_act = "models.detail",
            cancel_act = "models.index",
            download_act = "models.model_download",
            download_name = model_name,
            delete_act = "models.delete",
            form_name = 'Model Form', 
            is_multipart = True
        )
        return self.render("admin/model_detail.html",
                            form=form,
                            formCtrl=formCtrl)

    @expose("/model/download/<filename>")
    def model_download(self, filename):
        model_path = getFullPath(filename, 'static/model-upload')
        return send_file(model_path, 
                        attachment_filename=filename, 
                        as_attachment=True, 
                        mimetype='application/octet-stream')

    @expose("/delete/<int:_id>")
    def delete(self, _id):
        getDLModelById = DL_Model.query.get(_id)
        db.session.delete(getDLModelById)
        db.session.commit()
        flash('Model ' + getDLModelById.name + ' has been deleted!', 'success')
        return redirect(url_for('models.index'))