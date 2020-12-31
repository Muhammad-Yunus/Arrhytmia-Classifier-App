from .ecg_read_from_csv import read_from_csv
from .ecg_baseline_als import remove_baseline_als
from .ecg_normalizarion import min_max_normalization, scaler
from .ecg_rr_detection import rr_detector
from .ecg_upsampling_signals import upsampling_signals

from .ecg_add_awgn_noise import add_noise_to_signals
from .ecg_denoising_model import denoising_signal, read_adapfilt_model
from .ecg_classification import load_model_classification, predict_class

from . import pd
from . import pa
from . import os
from . import np
from . import resample_poly

import time

def preprocessing_unsplited(filename, path, fs):
    ECG = read_from_csv(filename, path, fs)
    ECG_ALS = remove_baseline_als(ECG)
    ECG_Norm = min_max_normalization(ECG_ALS)
    ECG_Norm = [np.array(item)[:,0] for item in ECG_Norm]
    if fs == 250:
        ECG_Norm = [resample_poly(item, 1, 5) for item in ECG_Norm] #downsampling from 250Hz to 50Hz
    return ECG_Norm

def preprocessing(filename, path, fs):
    ECG = read_from_csv(filename, path, fs)
    ECG_ALS = remove_baseline_als(ECG)
    ECG_Norm = min_max_normalization(ECG_ALS)
    ECG_split = rr_detector(ECG_Norm, fs)
    ECG_Split_250 = upsampling_signals(ECG_split, fs)
    #ECG_Scaler = scaler(ECG_Split_250)
    return ECG_Split_250

def save_splited_ecg(ECG_Split_250, filename, path):
    ECG_SPLIT_DF = pd.DataFrame(ECG_Split_250)
    ECG_SPLIT_DF = ECG_SPLIT_DF.fillna(0)
    ECG_SPLIT_DF.to_csv(os.path.join(path, filename), index=0, header=False)

def read_splited_ecg(filename, path):
    ECG_SPLIT_DF = pd.read_csv(os.path.join(path, filename), header=None)
    return ECG_SPLIT_DF

def split_sequence(filename, path="static\csv-upload",fs=25):
    print("[INFO] Start Preprocessing")
    ECG_Split_250 = preprocessing(filename, path=path, fs=fs)
    ECG_Unsplit = preprocessing_unsplited(filename, path=path, fs=fs)

    curr_fs = fs
    index = time.strftime("%Y%m%d_%H%M%S", time.localtime(time.time()))
    saved_filename_ecg_split = "%s_%sHz_%s" % (index, curr_fs, filename)
    saved_filename_ecg_unsplit = "unsplit_%s_%sHz_%s" % (index, curr_fs, filename)
    target_path = "app\static\csv-ecg-split"
    save_splited_ecg(ECG_Split_250, saved_filename_ecg_split, path=target_path)
    save_splited_ecg(ECG_Unsplit, saved_filename_ecg_unsplit, path=target_path)
    
    print("[INFO] Sequence Generated!")
    return os.path.exists(os.path.join(target_path, saved_filename_ecg_split)), saved_filename_ecg_split

def load_sequence(filename, path="static\csv-ecg-split"):
    ECG_DF = read_splited_ecg(filename, path=path)
    ECG_sequence = ECG_DF.iloc[:,:300].values
    ECG_sequence = ECG_sequence.reshape(len(ECG_sequence), ECG_sequence.shape[1],1)

    ECG_DF_UNSPLIT = read_splited_ecg("unsplit_" + filename, path=path)
    ECG_sequence_unsplit = ECG_DF_UNSPLIT.values
    ECG_sequence_unsplit = ECG_sequence_unsplit.reshape(len(ECG_sequence_unsplit), ECG_sequence_unsplit.shape[1],1)

    return ECG_sequence, ECG_sequence_unsplit

def load_model(filename, path="static\model-upload"):
    cnn_model = load_model_classification(filename, path=path)
    return cnn_model

def predict_sequence(cnn_model, single_sequence):
    single_sequence = np.array([single_sequence])
    try :
        result = predict_class(cnn_model, single_sequence)
        return result
    except :
        return None
