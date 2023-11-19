import socket
import time
import os
import sys

from threading import Thread
from secrets import public_ip, public_port, db_port

def sendDataToDb(data, ip, port):
    db_socket = socket.socket()  # instantiate
    try:
      db_socket.connect(("localhost", db_port))  # connect to the server

      db_socket.send(data.encode())

      db_socket.close()  # close the connection
    except ConnectionRefusedError:
      return

class TempSensorListener():

    def __init__(self, tempip, tempport) -> None:
        self.__runningfl = True
        self.tempPort = tempport
        self.tempIp = tempip
        self.dbPort = db_port
        self.dbIp = 'localhost'

    def start(self) :
        self.thread = Thread(target=self.__startTempListener)
        self.thread.start()
        return True

    def end(self) :
        self.__runningfl = False
        self.thread.join()

    def __startTempListener(self):
        server_socket = socket.socket()  # get instance
        server_socket.settimeout(3.0)

        server_socket.bind((self.tempIp, self.tempPort))
        server_socket.listen(2)

        while self.__runningfl:
            try:
                conn, address = server_socket.accept()  # accept new connection
                data = conn.recv(1024).decode()
                conn.close()
            except TimeoutError:
                time.sleep(5)
                continue
            except socket.timeout:
                time.sleep(5)
                continue

            sendDataToDb(data, self.dbIp, self.dbPort)

            time.sleep(5)

        server_socket.close()




if __name__ == '__main__':

    listener = TempSensorListener(public_ip, public_port)
    listener.start()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Terminating...")
        listener.end()
        print("Terminated successfully.")
        try:
            sys.exit(130)
        except SystemExit:
            os._exit(130)
