import eventlet
eventlet.monkey_patch()

import os
import json
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

import numpy as np
from flask import Flask, request 
from app.ecg_core.ecg_main_services import split_sequence, load_sequence
from app.ecg_core.ecg_main_services import load_model, predict_sequence

from app.models.dl_models import DL_Model

app = Flask(__name__)

def load_model_wrapper():
    model_record = DL_Model().query.filter_by(
                                    is_used = True
                                ).first()
    model_name = model_record.file_name
    print("[INFO] model name : %s" % model_name)
    if model_name :
        global model 
        model = load_model(model_name, path="app/static/model-upload")

@app.route('/', methods=['GET'])
def home():
    return "- ECG CORE API -"

@app.route('/ecg_split_sequence', methods=['GET'])
def ecg_split_sequence():
    filename = request.args.get('filename')
    fs = request.args.get('fs')
    print("[INFO] filename %s (%s)" % (filename, fs))
    if filename :
        result = split_sequence(filename, path="app/static/csv-upload", fs= int(fs) if fs is not None else 25)
        return dict(status = result[0], 
                    filename = result[1])
    else :
        return dict(status = False, 
                    filename = '')

@app.route('/ecg_load_sequence', methods=['GET'])
def ecg_load_sequence():
    filename = request.args.get('filename')
    
    print("[INFO] filename %s" % filename)
    result, result_unsplit = load_sequence(filename, path="app/static/csv-ecg-split")
    dtype = result.dtype
    print("[INFO] ndarray dtype %s" % dtype)

    result = result.tolist()
    result_unsplit = result_unsplit.tolist()
    response = json.dumps({"array": result, "array_unsplit" : result_unsplit, "dtype": str(dtype)})
    return response

@app.route('/ecg_predict_sequence', methods=['POST'])
def ecg_predict_sequence():
    
    single_sequence = np.array(request.json['sequence'])
    if 'model' in globals():
        result = predict_sequence(model, single_sequence)
        print(result)
        try :
            response = json.dumps(dict(label = result[0], 
                                description = result[1],
                                confidence = str(result[2])))
            return response
        except Exception as e: 
            print(e)
            response = json.dumps(dict(label = '', 
                                description = '',
                                confidence = 0.0))
            return response
    else :
        response = json.dumps(dict(label = '', 
                                description = '',
                                confidence = 0.0))
        return response

if __name__ == "__main__":
    load_model_wrapper()
    app.run(port=5001, debug=False, threaded=False)