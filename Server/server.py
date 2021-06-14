import cv2
import socket
from dotenv import load_dotenv
import os
import numpy
import pickle
from flask import Flask, Response
from flask.helpers import url_for
import threading
import atexit

load_dotenv(os.path.abspath(os.path.join(
    os.path.realpath(__file__), "../.env")))

SERVER_PORT = int(os.getenv("SERVER_PORT"))
SOCKET_HEADER_SIZE = int(os.getenv("SOCKET_HEADER_SIZE"))

VIDEO_STREAM_PORT = int(os.getenv("VIDEO_STREAM_PORT"))


def output(outputString):
    print(outputString)


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
        output("Start Receiver Thread")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(("", SERVER_PORT))
        self.sock.listen(True)

        output(f"Receiver Server Start On Port: {SERVER_PORT}")

        while self.isRun:
            self.frame = None

            try:
                conn, addr = self.sock.accept()
                output(f"Receive Connection From: {addr[0]}:{addr[1]}")
            except:
                output("Terminate Socket Accepting")

            try:
                while self.isRun:
                    length = int(ReceiverServer.recvall(
                        conn, SOCKET_HEADER_SIZE).decode())
                    data = ReceiverServer.recvall(conn, length)
                    self.frame = pickle.loads(data)
            except:
                output(f"Connection Lost: {addr[0]}:{addr[1]}")
        self.sock.close()

    def __del__(self):
        self.sock.close()
        output("Receiver Thread Stopped")


def init_app():
    receiverServer = ReceiverServer()

    receiverServer.start()
    atexit.register(receiverServer.stop)
    output(f"Streaming Video On Port: {VIDEO_STREAM_PORT}")
    app = Flask(__name__)

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

    @app.route('/video_stream')
    def video_stream():
        return Response(gen_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")

    return (app, receiverServer) if __name__ == "__main__" else app


if __name__ == "__main__":
    app = init_app()
    app[0].run(host="0.0.0.0", port=VIDEO_STREAM_PORT)
    app[1].stop()
