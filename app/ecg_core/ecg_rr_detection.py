from . import Detectors
from . import find_peaks
from . import np

def rr_detector(ECG_Norm, fs=20, pad_size=24):
    detectors = Detectors(fs)
    ECG_split = []
    for data in ECG_Norm :
        data = np.array(data)
        if fs != 250 :
            h = np.mean(data[:,0]) + np.std(data[:,0])
            r_peaks = find_peaks(data[:,0], height=h)[0]
        else :
            r_peaks = detectors.christov_detector(data)
        RRs = np.diff(r_peaks)
        RRs_med = np.median(RRs)
        if not np.isnan(RRs_med) :
            for rp in r_peaks :
                split = data[:,0][rp : rp + int(RRs_med * 1.2)] 
                ECG_split.append(split)
    return ECG_split