import json
import sqlite3
import socket
import time
import os
import sys

from threading import Thread
from secrets import db_port


def updateDB(request):
    if ("dbname" not in request.keys() or 
        "dsname" not in request.keys() or 
        len(request.keys()) < 3):
        print("wrong format")
        return
    dbname = request['dbname']
    dsname = request['dsname']
    params = [elem for elem in request.keys() if elem not in ('dbname', 'dsname')]
    values = ["'{}'".format(request[elem]) for elem in params]

    print(request)


    con = sqlite3.connect("./data/"+dbname)
    cur = con.cursor()

    list_of_ds = [x[0] for x in cur.execute("SELECT name FROM sqlite_master").fetchall()]

    print(list_of_ds)
    if list_of_ds != None and dsname not in list_of_ds:
        print("Adding new database {}".format(dsname))
        cur.execute("CREATE TABLE {} ( {} )".format(dsname, " TEXT,".join(params)+" TEXT"))
        #dtm TIMESTAMP, temperature REAL, humidity REAL, desc TEXT

    cur.execute("INSERT INTO {} VALUES ({})".format(dsname, ", ".join(values)))

    con.commit()
    cur.close()
    con.close()


class DbUpdater:

    def __init__(self) -> None:
        self.__runningfl = True
    
    def start(self) :
        self.thread = Thread(target=self.__RequestListener)
        self.thread.start()
        return True
    
    def end(self) :
        self.__runningfl = False
        self.thread.join()

    def __RequestListener(self) -> None:

        port = db_port  # initiate port no above 1024
        server_socket = socket.socket()  # get instance
        server_socket.settimeout(3.0)
        
        server_socket.bind(("localhost", port))
        server_socket.listen(2)

        while self.__runningfl:
            try:
                conn, address = server_socket.accept()  # accept new connection
                data = conn.recv(1024).decode()

                conn.close()
            except TimeoutError:
                time.sleep(5)
                continue
            except socket.error:
                time.sleep(5)
                continue

            try:
                data_parsed = json.loads(data)
            except json.decoder.JSONDecodeError:
                print("Json has wrong format")
                continue

            updateDB(data_parsed)

            time.sleep(5)

        server_socket.close()

if __name__ == '__main__':
    dbupdate = DbUpdater()
    dbupdate.start()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Terminating...")
        dbupdate.end()
        print("Terminated successfully.")
        try:
            sys.exit(130)
        except SystemExit:
            os._exit(130)

