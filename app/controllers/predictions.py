from . import send_file, request, redirect, url_for
from . import BaseView, BaseViewSU, expose
from . import db, current_user
from . import flash
from . import os

from app.models.predictions import Prediction
from app.views.predictions import PredictionsForm

from .table_utils import GetTableHeader, getTableRecords, initTableRecords


class PredictionRoute(BaseViewSU):
    @expose("/", methods=["GET", "POST"])
    def index(self):

        # define initial variable
        page, per_page, table_search, search_key, _col, _type, sort_type = initTableRecords()


        # Create Table Record
        filters = ['label']
        tableRecords, min_page, max_page, count = getTableRecords(Prediction, search_key, filters, sort_type, _col, page, per_page)

        # Create Table Header
        col_exclude = ['data', 'raw']
        sort_exclude = ['id']
        overide_label = dict(
            id = 'No'
        )
        tableHeader = GetTableHeader(Prediction, col_exclude, sort_exclude, overide_label)

        # Create Header Control
        headerCtrl = dict(
            name = 'Prediction',
            is_search = True,
            search_act = 'predictions.index',
            table_search = table_search,
            is_export = False,
            export_act = 'predictions.download',
            export_filename = 'Export - predictions.csv',
            sort_act = 'predictions.index',
            detail_act = 'predictions.detail', 
            is_add_new = False
        )

        # Create Footer Control
        footerCtrl = dict(
            min_page=min_page, 
            max_page=max_page, 
            count=count,
            _type=_type,
            _col=_col,
            pagination_act = 'predictions.index'
        )

        print(headerCtrl)
        return self.render('admin/predictions.html', 
                            tableRecords=tableRecords, 
                            tableHeader=tableHeader,
                            headerCtrl=headerCtrl,
                            footerCtrl=footerCtrl
                        )

    @expose("/detail/<int:_id>", methods=['GET'])
    def detail(self, _id):
        form = PredictionsForm()
        getPredictionById = PredictionsForm.query.get(_id)

        if request.method == 'GET' and getPredictionById:
            form.label.data = getPredictionById.label
            form.confidence.data = getPredictionById.confidence

        inputField = ['label', 'confidence']
        submitField = []
        indexField = ['id']

        formCtrl = dict(
            _id=_id,
            inputField = inputField,
            submitField = submitField,
            indexField=indexField,
            form_act = 'predictions.detail',
            form_name = 'Prediction Result',
            cancel_act = "predictions.index",
        )
        return self.render("admin/prediction_detail.html",
                            form=form,
                            formCtrl=formCtrl)