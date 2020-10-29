from flask_socketio import SocketIO, emit
from flask import render_template, session, request
from app import app, eventlet

async_mode = None
socketio = SocketIO(app, async_mode=async_mode)

class Worker(object):

    switch = False
    unit_of_work = 0

    def __init__(self, socketio):
        self.socketio = socketio
        self.switch = False
        self.EcgData = []

    def store_data(self, EcgData):
        self.EcgData.append(EcgData)

    def do_work(self):
        """
        Main task | Stream ECG Data to client
        """
        while self.switch:

            if len(self.EcgData) > 0 :
                ECG_buffer = self.EcgData[0]
                del self.EcgData[0]
            else :
                ECG_buffer = [0]

            print("[INFO] Background thread sending... %d/%d" % (len(ECG_buffer), len(self.EcgData)))
            socketio.sleep(0.2)
            socketio.emit('ecg_receive',
                        {'data': ECG_buffer, 
                        'async' : socketio.async_mode,
                        'count': 1},
                        namespace='/arrhytmia')

    def stop(self):
        self.switch = False

    def start(self):
        self.switch = True

    def is_start(self):
        return self.switch

@socketio.on('connect', namespace='/arrhytmia')
def connect():
    if 'worker' not in globals() :
        global worker
        worker = Worker(socketio)
        print("[INFO] connected, create worker...")
    else :
        print("[INFO] -------- connect ----------")

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
            print("[INFO] Starting thread ... ")
            emit('ecg_info', 'start sending data...', broadcast=True)
            socketio.start_background_task(target=worker.do_work)
        else :
            print("[INFO] Thread already started ... ")

    if message['data'] == "stop" :
        worker.stop()
        print("[INFO] Stoping thread ... ")

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", debug=True)
    #app.run(host="0.0.0.0", debug=False)
