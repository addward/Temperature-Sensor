import socket
import time
import os
import sys

from threading import Thread
from secrets_local import public_ip, public_port, db_port
from DbUpdater import readDB

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
            n1_ds = readDB(dbname = "Plants.db", request = "select count(1) from waterplant where plantnum='1'")
            n1 = 0
            if n1_ds != None:
                n1 = min(n1_ds[0][0], 9)
            n2_ds = readDB(dbname = "Plants.db", request = "select count(1) from waterplant where plantnum='2'")
            n2 = 0
            if n2_ds != None:
                n2 = min(n1_ds[0][0], 9)
            n3_ds = readDB(dbname = "Plants.db", request = "select count(1) from waterplant where plantnum='3'")
            n3 = 0
            if n3_ds != None:
                n3 = min(n1_ds[0][0], 9)

            request = "{}{}{}".format(n1,n2,n3)
            try:
                conn, address = server_socket.accept()  # accept new connection
                data = conn.recv(1024).decode()
                print("Send: {}".format(request))
                conn.send(request.encode())
                time.sleep(5)
                conn.close()
                readDB(dbname = "Plants.db", request = "delete from waterplant")
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
