import socketio
import time 

sio = socketio.Client()

pulse = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
            0.08, 0.18, 0.08, 0, 0, 0, 0, 0, 0, -0.04, 
            -0.08, 0.3, 1.1, 0.3, -0.17, 0.00, 0.04, 0.04, 
            0.05, 0.05, 0.06, 0.07, 0.08, 0.10, 0.11, 0.11, 
            0.10, 0.085, 0.06, 0.04, 0.03, 0.01, 0.01, 0.01, 
            0.01, 0.02, 0.03, 0.05, 0.05, 0.05, 0.03, 0.02, 0, 0, 0]
ECG_buffer = [pulse for i in range(100)]

@sio.on('connect', namespace='/arrhytmia')
def on_connect():
    print("[INFO] Publisher connected to server...")
    sio.emit('publisher_event', "<ECG Sensor Simulator>", namespace='/arrhytmia')

@sio.on('disconnect', namespace='/arrhytmia')
def on_disconnect():
    print("[INFO] Publisher disconnected from server...")

if __name__ == '__main__':
    sio.connect('http://localhost:5000', namespaces=['/arrhytmia'])

    while len(ECG_buffer) > 0 :
        output = ECG_buffer[0]
        del ECG_buffer[0]
        sio.emit('incoming_stream', {'data' : output}, namespace='/arrhytmia')
        print("[INFO] Publisher send data to server : ", len(output), "/", len(ECG_buffer))
        time.sleep(1)
    else :
        sio.disconnect()
        print("[INFO] Publisher close connection to server...")
