import cv2
import socket
from dotenv import load_dotenv
import os
import numpy
import pickle
from flask import Flask, Response
from flask.helpers import url_for

load_dotenv(os.path.abspath(os.path.join(
    os.path.realpath(__file__), "../.env")))

CLIENT_NAME = os.getenv("CLIENT_NAME")

SERVER_PORT = int(os.getenv("SERVER_PORT"))
SOCKET_HEADER_SIZE = int(os.getenv("SOCKET_HEADER_SIZE"))

VIDEO_STREAM_PORT = int(os.getenv("VIDEO_STREAM_PORT"))

CAMERA_NAME = os.getenv("CAMERA_NAME")


def output(outputString):
    print(outputString)


def recvall(sock, count):
    buffer = b''
    while count:
        data = sock.recv(count)
        if not data:
            return None
        buffer += data
        count -= len(data)
    return buffer


def init_app():
    app = Flask(__name__)

    def gen_frames():
        lastFrame = numpy.zeros([1, 1, 3], dtype=numpy.uint8)
        lastFrame.fill(0)
        while True:
            try:
                sock = socket.socket()
                sock.connect(("localhost", SERVER_PORT))

                data = pickle.dumps(f"1{CLIENT_NAME}")
                sock.send(str(len(data)).ljust(SOCKET_HEADER_SIZE).encode())
                sock.send(data)

                data = pickle.dumps(f"{CAMERA_NAME}")
                sock.send(str(len(data)).ljust(SOCKET_HEADER_SIZE).encode())
                sock.send(data)

                length = int(recvall(
                    sock, SOCKET_HEADER_SIZE).decode())
                frame = pickle.loads(recvall(sock, length))
            except:
                frame = lastFrame

            lastFrame = frame
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
                <img style="height:calc(100vh - 79.88px);object-fit:contain;object-position:left top" src="{url_for('video_stream')}">
            </div>
        </body>
        '''

    @app.route('/video_stream')
    def video_stream():
        return Response(gen_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")

    return app


if __name__ == "__main__":
    app = init_app()
    output(f"Streaming Video On Port: {VIDEO_STREAM_PORT}")
    app.run(host="0.0.0.0", port=VIDEO_STREAM_PORT)
