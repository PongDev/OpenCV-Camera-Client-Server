import socket
from dotenv import load_dotenv
import os
import numpy
import pickle
import threading

load_dotenv(os.path.abspath(os.path.join(
    os.path.realpath(__file__), "../.env")))

SERVER_PORT = int(os.getenv("SERVER_PORT"))
SOCKET_HEADER_SIZE = int(os.getenv("SOCKET_HEADER_SIZE"))

isRun = True


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


class Client(threading.Thread):

    def __init__(self, sock, addr):
        threading.Thread.__init__(self)

        Client.threadCount += 1
        self.sock = sock
        self.addr = addr
        output(
            f"Camera Client {self.addr[0]}:{self.addr[1]} Created: {Client.threadCount} Current Client(s)")

        self.start()

    def __del__(self):
        if (self.clientName in Client.clientNameData):
            Client.clientNameData.pop(self.clientName)
        self.sock.close()

        Client.threadCount -= 1
        output(
            f'Camera Client {self.addr[0]}:{self.addr[1]} Name: {self.clientName if self.clientName != None else "Unknown"} Destroyed: {Client.threadCount} Current Client(s)')

    def stop(self):
        if (self.clientName in Client.clientNameData):
            Client.clientNameData.pop(self.clientName)
        self.sock.close()

    def run(self):
        global isRun

        length = int(recvall(
            self.sock, SOCKET_HEADER_SIZE).decode())
        data = pickle.loads(recvall(self.sock, length))
        self.clientMode = int(data[0])
        self.clientName = data[1:]

        output(f"Client Name: {self.clientName}, Mode: {self.clientMode}")

        if (self.clientName in Client.clientNameData):
            output(
                f"Error: Duplicate Client Name: {self.clientName}, Mode: {self.clientMode}")
            self.stop()
            return
        else:
            Client.clientNameData[self.clientName] = {}

        if (self.clientMode == 0):
            try:
                while isRun:
                    length = int(recvall(
                        self.sock, SOCKET_HEADER_SIZE).decode())
                    data = recvall(self.sock, length)
                    Client.clientNameData[self.clientName]["frame"] = pickle.loads(
                        data)
            except:
                output(f"Connection Lost: {self.addr[0]}:{self.addr[1]}")
        elif (self.clientMode == 1):
            length = int(recvall(
                self.sock, SOCKET_HEADER_SIZE).decode())
            data = recvall(self.sock, length)
            requestClientFrameName = pickle.loads(data)
            if (requestClientFrameName in Client.clientNameData and "frame" in Client.clientNameData[requestClientFrameName]):
                data = Client.clientNameData[requestClientFrameName]["frame"]
            else:
                data = numpy.zeros([1, 1, 3], dtype=numpy.uint8)
                data.fill(0)
            data = pickle.dumps(data)
            self.sock.send(str(len(data)).ljust(
                SOCKET_HEADER_SIZE).encode())
            self.sock.send(data)

        if (self.clientName in Client.clientNameData):
            Client.clientNameData.pop(self.clientName)


Client.threadCount = 0
Client.clientNameData = {}


def run():
    global isRun

    output("Start Camera Server")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("", SERVER_PORT))
    sock.listen()

    output(f"Camera Server Start On Port: {SERVER_PORT}")

    while isRun:
        try:
            conn, addr = sock.accept()
            output(f"Receive Connection From: {addr[0]}:{addr[1]}")
            Client(conn, addr)
        except:
            output("Terminate Socket Accepting")
            isRun = False
    sock.close()


run()
