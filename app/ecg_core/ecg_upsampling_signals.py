from . import np
from . import resample_poly

def upsampling_twice(data):
    # upsampling interpolation
    result = np.zeros(2*len(data)-1)
    result[0::2] = data
    result[1::2] = (data[1:] + data[:-1]) / 2
    return result

def upsampling_single_signal(data, fs, new_fs = 125):
    if fs != 125 :
        data = np.array(data)
        data = resample_poly(data, new_fs, fs)
    pad = np.zeros(150)
    n_max = len(data) if len(data) <= 150 else 150
    pad[:n_max] = data[:n_max]
    return pad

def upsampling_signals(ECG_split, fs):
    ECG_Split_125 = []
    for data in ECG_split :
        data = np.array(data)
        data = upsampling_single_signal(data, fs) # upsampling signal to 125hz
        ECG_Split_125.append(data)
    return ECG_Split_125
