import unittest
import os
import json
import sqlite3

import DbUpdater, TempSensorListener
from secrets import db_port

# DataBase updater

class Test(unittest.TestCase):
    def test_add_data_to_db(self):
        database = "mydb.db"
        dsname = "testDs"
        request = '{{"dbname":"{}","dsname":"{}","color":"gold","temp":null,"hum":123,"string":"Hello World","test":""}}'.format(database, dsname)
        
        DbUpdater.updateDB(json.loads(request))

        con = sqlite3.connect("./data/"+database)
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        row = cur.execute("SELECT * from {}".format(dsname)).fetchone()
        actual = {key: row[key] for key in row.keys()}

        con.close()

        expected = {'color':"gold","temp":"None","hum":"123","string":"Hello World","test":""}
        self.assertEqual(actual, expected)

        os.remove("./data/" + database)

    def test_bad_syntax1(self):
        database = "mydb.db"
        request = '{{"dbname":"{}"}}'.format(database)
        
        DbUpdater.updateDB(json.loads(request))

        self.assertEqual(False, os.path.exists("./data/{}".format(database)))

    def test_bad_syntax2(self):
        database = "mydb.db"
        dsname = "testDs"
        request = '{{"dbname":"{}","dsname":"{}"}}'.format(database, dsname)
        
        DbUpdater.updateDB(json.loads(request))

        self.assertEqual(False, os.path.exists("./data/{}".format(database)))

    # Add database record via socket

    def test_db_socket(self):

        updater = DbUpdater.DbUpdater()
        updater.start()
        database = "mydb.db"
        dsname = "testDs"
        request = '{{"dbname":"{}","dsname":"{}","color":"gold","temp":null,"hum":123,"string":"Hello World","test":""}}'.format(database, dsname)
        TempSensorListener.sendDataToDb(request,"localhost",db_port)
        updater.end()

        con = sqlite3.connect("./data/"+database)
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        row = cur.execute("SELECT * from {}".format(dsname)).fetchone()
        actual = {key: row[key] for key in row.keys()}

        con.close()

        expected = {'color':"gold","temp":"None","hum":"123","string":"Hello World","test":""}
        self.assertEqual(actual, expected)

        os.remove("./data/" + database)

    def test_db_socket_badsyntax(self):

        updater = DbUpdater.DbUpdater()
        updater.start()
        database = "mydb.db"
        dsname = "testDs"
        request = '{{"dbname":"{}","dsname":"{}"}}'.format(database, dsname)
        TempSensorListener.sendDataToDb(request,"localhost",db_port)
        updater.end()

        self.assertEqual(False, os.path.exists("./data/{}".format(database)))

