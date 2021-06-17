import cv2
import socket
from dotenv import load_dotenv
import os
import numpy
import pickle
from datetime import datetime
import time

load_dotenv(os.path.abspath(os.path.join(
    os.path.realpath(__file__), "../.env")))

CLIENT_NAME = os.getenv("CLIENT_NAME")
SERVER_IP = os.getenv("SERVER_IP")
SERVER_PORT = int(os.getenv("SERVER_PORT"))
SOCKET_HEADER_SIZE = int(os.getenv("SOCKET_HEADER_SIZE"))
CAMERA_ROTATE = int(os.getenv("CAMERA_ROTATE"))
CAPTURE_FPS = int(os.getenv("CAPTURE_FPS"))

print(f"Start Client Name: {CLIENT_NAME}")
print(f"Destination Server {SERVER_IP}:{SERVER_PORT}")

while True:
    sock = socket.socket()
    video = cv2.VideoCapture(0)
    try:
        sock.connect((SERVER_IP, SERVER_PORT))

        print(f"Connect Server: {SERVER_IP}:{SERVER_PORT}")

        data = pickle.dumps(f"0{CLIENT_NAME}")
        sock.send(str(len(data)).ljust(SOCKET_HEADER_SIZE).encode())
        sock.send(data)

        timestamp = 0

        while True:
            ret, frame = video.read()
            if (time.time() - timestamp >= 1 / CAPTURE_FPS):
                timestamp = time.time()
                if (CAMERA_ROTATE in [cv2.ROTATE_180, cv2.ROTATE_90_CLOCKWISE, cv2.ROTATE_90_COUNTERCLOCKWISE]):
                    frame = cv2.rotate(frame, CAMERA_ROTATE)
                frame = cv2.putText(frame, datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"), (0, frame.shape[0]), cv2.FONT_HERSHEY_PLAIN, 1.5, (255, 255, 255), 2)
                data = pickle.dumps(numpy.array(frame))
                sock.send(str(len(data)).ljust(SOCKET_HEADER_SIZE).encode())
                sock.send(data)
    except:
        print("Connection Lost")
    video.release()
    sock.close()
