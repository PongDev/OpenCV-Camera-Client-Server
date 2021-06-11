import cv2
import socket
from dotenv import load_dotenv
import os
import numpy
import pickle
from flask import Flask, Response
from flask.helpers import url_for
import threading

load_dotenv()

SERVER_PORT = int(os.getenv("SERVER_PORT"))
SOCKET_HEADER_SIZE = int(os.getenv("SOCKET_HEADER_SIZE"))

VIDEO_STREAM_PORT = int(os.getenv("VIDEO_STREAM_PORT"))


class ReceiverServer (threading.Thread):

    @staticmethod
    def recvall(sock, count):
        buffer = b''
        while count:
            data = sock.recv(count)
            if not data:
                return None
            buffer += data
            count -= len(data)
        return buffer

    def __init__(self):
        threading.Thread.__init__(self)
        self.isRun = True

    def stop(self):
        self.isRun = False
        self.sock.close()

    def getFrame(self):
        return self.frame

    def run(self):
        print("Start Receiver Thread")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(("", SERVER_PORT))
        self.sock.listen(True)

        print(f"Receiver Server Start On Port: {SERVER_PORT}")

        while self.isRun:
            self.frame = None

            try:
                conn, addr = self.sock.accept()
                print(f"Receive Connection From: {addr[0]}:{addr[1]}")
            except:
                print("Terminate Socket Accepting")

            try:
                while self.isRun:
                    length = int(ReceiverServer.recvall(
                        conn, SOCKET_HEADER_SIZE).decode())
                    data = ReceiverServer.recvall(conn, length)
                    self.frame = pickle.loads(data)
            except:
                print(f"Connection Lost: {addr[0]}:{addr[1]}")
        self.sock.close()

    def __del__(self):
        self.sock.close()
        print("Receiver Thread Stopped")


receiverServer = ReceiverServer()
receiverServer.start()

app = Flask(__name__)


@app.route('/')
def index():
    return f'''
    <body style="margin:0">
        <div class="container" style="height:100vh;display:flex;flex-direction:column">
            <h1>Camera</h1>
            <img style="object-fit:contain;object-position:left" src="{url_for('video_stream')}">
        </div>
    </body>
    '''


def gen_frames():
    while True:
        frame = receiverServer.getFrame()
        if (type(frame) == type(None)):
            frame = numpy.zeros([1, 1, 3], dtype=numpy.uint8)
            frame.fill(0)
        ret, frame = cv2.imencode('.jpg', frame)
        frame = frame.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_stream')
def video_stream():
    return Response(gen_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")


print(f"Streaming Video On Port: {VIDEO_STREAM_PORT}")
app.run(port=VIDEO_STREAM_PORT)
receiverServer.stop()
