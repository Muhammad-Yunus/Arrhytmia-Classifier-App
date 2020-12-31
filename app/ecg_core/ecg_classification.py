from . import load_model
from . import os
from . import np 

def load_model_classification(filename, path=""):
    model = load_model(os.path.join(path, filename))
    return model

def predict_class(model, data):
    result = model.predict(data)
    label_desc = dict(
        AF = 'Atrial Fibriliantion',
        N = 'Normal')
    label = ['AF', 'N']
    label_idx = np.argmax(result)
    predicted_label = label[label_idx]
    predicted_desc =  label_desc[predicted_label]
    confidence = result[0][label_idx]
    return predicted_label, predicted_desc, confidence