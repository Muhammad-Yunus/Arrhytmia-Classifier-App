import pickle
from .AdaptiveFilterWrapper import adapfilt_modeler
from . import np
from . import os

def read_adapfilt_model(filename, path=""):
    with open(os.path.join(path, filename), 'rb') as in_name:
        model = pickle.load(in_name)
        return model

def denoising_signal(model, noised_signal):
    denoised_signal = model.transform(noised_signal)
    return denoised_signal