from . import MaxAbsScaler
from . import timedelta, datetime
from . import np

def min_max_normalization(ECG_ALS):
    scaler = MaxAbsScaler()
    ECG_Norm = []

    for als in ECG_ALS :
        als = np.expand_dims(als, 1)
        scaler = scaler.fit(als)
        
        als_norm = scaler.transform(als) 
        ECG_Norm.append(als_norm)
    return ECG_Norm

# scale data from 0 to 1
def scaler(X):
    res = []
    for x in X :
        idx = np.max(np.nonzero(x))
        x[idx+1:] = x.min()
        res.append((x - x.min())/(x.max() - x.min()))
    return np.array(res)

