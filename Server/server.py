import cv2
import socket
from dotenv import load_dotenv
import os
import pickle

load_dotenv()

SERVER_PORT = int(os.getenv("SERVER_PORT"))
SOCKET_HEADER_SIZE = int(os.getenv("SOCKET_HEADER_SIZE"))


def recvall(sock, count):
    buffer = b''
    while count:
        data = sock.recv(count)
        if not data:
            return None
        buffer += data
        count -= len(data)
    return buffer


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(("", SERVER_PORT))
sock.listen(True)

print(f"Server Start On Port: {SERVER_PORT}")

while True:
    conn, addr = sock.accept()

    print(f"Receive Connection From: {addr[0]}:{addr[1]}")

    try:
        while True:
            length = int(recvall(conn, SOCKET_HEADER_SIZE).decode())
            data = recvall(conn, length)
            frame = pickle.loads(data)
            cv2.imshow("Frame", frame)
            cv2.waitKey(1)
    except:
        print(f"Connection Lost: {addr[0]}:{addr[1]}")
    cv2.destroyAllWindows()
sock.close()
