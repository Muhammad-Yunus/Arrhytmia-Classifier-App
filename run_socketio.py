from flask_socketio import SocketIO, emit
from flask import render_template, session
from app import app, eventlet, build_sample_db
import requests
import json 
import numpy as np
import time 

async_mode = None
socketio = SocketIO(app, async_mode=async_mode)

class Predictor(object):
    def __init__(self, socketio):
        self.sequences = []
        self.switch = False
        self.socketio = socketio
        self.idx_seq = 0
        self.len_seq = 0

    def store_data(self, Sequences):
        self.sequences = Sequences
        self.len_seq = len(Sequences)

    def predict(self):
        url = "http://127.0.0.1:5001/ecg_predict_sequence"
        while self.switch :
            if len(self.sequences) > 0 :
                seq = self.sequences[0]
                self.sequences = self.sequences[1:]

                response = requests.post(url, json={
                                                    'sequence': seq.tolist()
                                                    }).content
                dict_response = json.loads(response)
                label = dict_response['label']
                confidence = float(dict_response['confidence'])*100

                print("[INFO] Background thread prediction : %s (%.2f)" % (label, confidence))
                self.socketio.emit('curr_sequence_receive',
                            {'data': seq.tolist(), 
                            'async' : self.socketio.async_mode,
                            'confidence': confidence,
                            'index' : self.idx_seq,
                            'length' : self.len_seq,
                            'label' : label},
                            namespace='/arrhytmia')
            self.socketio.sleep(1)
            self.idx_seq += 1

    def stop(self):
        self.idx_seq = 0
        self.switch = False
        self.sequences = []
        print("[INFO] predictor stopped!")

    def pause(self):
        self.switch = False
        print("[INFO] predictor paused!")

    def start(self):
        self.switch = True

    def is_start(self):
        return self.switch

class Worker(object):

    switch = False
    unit_of_work = 0

    def __init__(self, socketio):
        self.socketio = socketio
        self.switch = False
        self.EcgData = []
        self.ECG_buffer = []

    def store_data(self, EcgData):
        self.EcgData.append(EcgData)

    def do_work(self):
        """
        Main task | Stream ECG Data to client
        """
        while self.switch:

            if len(self.EcgData) > 0 :
                self.ECG_buffer = self.EcgData[0]
                del self.EcgData[0]
            else :
                self.ECG_buffer = [0]

            #print("[INFO] Background thread sending to client... %d/%d" % (len(self.ECG_buffer), len(self.EcgData)))
            socketio.sleep(0.2)
            socketio.emit('ecg_receive',
                        {'data': self.ECG_buffer, 
                        'async' : socketio.async_mode,
                        'count': 1},
                        namespace='/arrhytmia')

    def stop(self):
        self.switch = False
        self.EcgData = []
        self.ECG_buffer = []
        print("[INFO] worker stopped!")

    def pause(self):
        self.switch = False
        print("[INFO] worker paused!")

    def start(self):
        self.switch = True

    def is_start(self):
        return self.switch

@socketio.on('connect', namespace='/arrhytmia')
def connect():
    if 'worker' not in globals() :
        global worker
        worker = Worker(socketio)
    if 'predictor' not in globals():
        global predictor
        predictor = Predictor(socketio)
    print("[INFO] connected, create worker & predictor...")

@socketio.on('publisher_event', namespace='/arrhytmia')
def publisher_message(message):
    print("[INFO] Publisher connect to server :", message)

@socketio.on('incoming_stream', namespace='/arrhytmia')
def incoming_message(message):
    worker.store_data(message['data'])
    print("[INFO] Receive data from publisher :", len(message['data']))

@socketio.on('ecg_event', namespace='/arrhytmia')
def test_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('ecg_info',
         {'data': message['data'], 'count': session['receive_count']}, broadcast=True)


@socketio.on('start_event', namespace='/arrhytmia')
def test_connect(message):
    if message['data'] == "start" :
        if not worker.is_start() :
            worker.start()
            print("[INFO] Starting thread for worker... ")
            emit('ecg_info', 'worker start sending data...', broadcast=True)
            socketio.start_background_task(target=worker.do_work)
        else :
            print("[INFO] Worker thread already started ... ")

        if not predictor.is_start() :
            predictor.start()
            print("[INFO] Starting thread for predictor... ")
            emit('ecg_info', 'predictor start sending data...', broadcast=True)
            socketio.start_background_task(target=predictor.predict)
        else :
            print("[INFO] Predictor thread already started ... ")     
        
        # emiting data to input stream
        #print("[INFO] data source %s" %  message['source'])
        if message['source'].find("://") < 0 :
            try :
                url = "http://127.0.0.1:5001/ecg_load_sequence"
                response = requests.get(url, params={
                                                    'filename': message['source']
                                                    }).content
                dict_response = json.loads(response)
                ecg_data = np.array(dict_response['array'])
                ecg_data_unsplit = np.array(dict_response['array_unsplit'])
                print("\n\n")
                print("[INFO] Receive data stream from API,")
                print("data dtype :", dict_response['dtype'])
                print("data split size :", ecg_data.shape , ecg_data.dtype)
                print("data unsplit size :", ecg_data_unsplit.shape , ecg_data_unsplit.dtype)
                print("\n\n")

                for i, single_ecg in enumerate(ecg_data_unsplit) :
                    single_ecg = single_ecg[:,0]
                    ids = np.where(single_ecg != 0.0)[0]
                    single_ecg = single_ecg[:ids[-1] + 1]

                    print("[INFO] transmiting data to thread with shape :", single_ecg.shape)
                    worker.store_data(single_ecg.tolist())

                # ---------- Predictor ---------------------
                predictor.store_data(ecg_data)

            except Exception as e:
                print("\x1b[0;31;40m [ERROR] ", e, "\x1b[0m\n\n")
        else :
            print("[INFO] connecting to stream interface %s" % message['source'])

    if message['data'] == "stop" :
        worker.stop()
        predictor.stop()
        print("[INFO] Stoping thread ... ")

    if message['data'] == "pause" :
        worker.pause()
        predictor.pause()
        print("[INFO] Pause thread ... ")

if __name__ == '__main__':
    #build_sample_db()
    socketio.run(app, host="0.0.0.0", debug=False)
    #app.run(host="0.0.0.0", debug=False)
