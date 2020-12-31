from . import np

def add_awgn_noise(signal, target_noise_db = -30):
    
    mean_noise = 0
    target_noise_watts = 10 ** (target_noise_db / 10)
    sigma = np.sqrt(target_noise_watts)
    
    noise = np.random.normal(mean_noise, sigma, len(signal))

    return (signal+noise)

def add_noise_to_signals(ECG_SPLIT_DF):
    signal = ECG_SPLIT_DF.iloc[:,:300].values
    noised_signal = ECG_SPLIT_DF.iloc[:,:300].apply(add_awgn_noise, axis=1).values
    return noised_signal, signal