from . import BaseViewSU, expose
from . import func
from . import db

from app.models.ecgs import Ecg
from app.models.dl_models import DL_Model
from app.models.predictions import Prediction

class DashboardRoute(BaseViewSU):
    @expose("/", methods=["GET", "POST"])
    def index(self):
        ecgs = Ecg().query.filter_by(
                                    is_procced = True
                                ).all()
        available_sequences= [ ecg.procced_name for ecg in ecgs] 
        fs_sequence = {}
        for ecg in ecgs:
            fs_sequence[ecg.procced_name] =  ecg.fs

        ECG_sample_count = len(available_sequences)
        Model_count = DL_Model().query.count()
        Feature_count = 300
        Avg_prediction = db.session.query(func.avg(Prediction.confidence)).first()[0]
        return self.render('admin/dashboard.html',
                            available_sequences = available_sequences,
                            ECG_sample_count = ECG_sample_count,
                            Model_count = Model_count,
                            Feature_count = Feature_count,
                            Avg_prediction = Avg_prediction,
                            fs_sequence = fs_sequence
                            )