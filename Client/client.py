import cv2
import socket
from dotenv import load_dotenv
import os
import numpy
import pickle

load_dotenv()

SERVER_IP = os.getenv("SERVER_IP")
SERVER_PORT = int(os.getenv("SERVER_PORT"))
SOCKET_HEADER_SIZE = int(os.getenv("SOCKET_HEADER_SIZE"))

sock = socket.socket()
sock.connect((SERVER_IP, SERVER_PORT))

print(f"Connect Server: {SERVER_IP}:{SERVER_PORT}")

video = cv2.VideoCapture(0)

while True:
    ret, frame = video.read()
    data = pickle.dumps(numpy.array(frame))
    sock.send(str(len(data)).ljust(SOCKET_HEADER_SIZE).encode())
    sock.send(data)
    cv2.waitKey(1)
video.release()
cv2.destroyAllWindows()
sock.close()
