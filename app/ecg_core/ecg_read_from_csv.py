from . import pd
from . import os

def read_from_csv(filename, path="../static/csv-upload/", fs=25, is_splited=True):
    ECG = pd.read_csv(os.path.join(path, filename), skiprows = [0])
    ECG.columns = ['Time', 'ECG']
    ECG["Idx_Time"] = pd.to_datetime(ECG["Time"]) 
    ECG.index = ECG["Idx_Time"]
    if fs == 125 :
        if is_splited :
            # reduce sampling rate from 250Hz to 125Hz     
            ECG = ECG.iloc[::2]
        ECG[ECG['ECG'] > 2] = 2
        ECG[ECG['ECG'] < -2] = -2
    ECG.drop('Idx_Time', axis=1, inplace=True)
    ECG.drop('Time', axis=1, inplace=True)
    return ECG
