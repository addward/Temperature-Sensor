import time
import threading
import sqlite3
import os

from concurrent.futures import ThreadPoolExecutor

class database(object):

    def __init__(self, filepath, dataset, t_listen, callback_func) -> None:
        self._filepath = filepath
        self._dataset = dataset
        self._last_upd_time = time.ctime(os.path.getmtime(filepath))
        
        self._listener_period = t_listen
        self._last_num_of_rows = 0
        self._callback_func = callback_func
        self._enable_listener = True

        self._upd_listener_thread_pool = ThreadPoolExecutor(max_workers=1)

        self._listener_future = \
            self._upd_listener_thread_pool.submit(self._update_listener)

    def _update_listener(self) -> int:
        while (self._enable_listener):
            tmp_time  = time.ctime(os.path.getmtime(self._filepath))
            if (self._last_upd_time != tmp_time):
                print("The file was updated: ", self._last_upd_time)
                self._last_upd_time = tmp_time
                self._callback_func()
            time.sleep(self._listener_period)
        return 0

    def getCursor(self, list_of_variables) -> sqlite3.Cursor:

        _connection = sqlite3.connect(self._filepath)
        _cursor = _connection.cursor()

        if self._last_num_of_rows == 0:
            """ [0][0] because the output has a form of [(n_of_rows,)] """
            self._last_num_of_rows = \
                _cursor.execute("SELECT count(1) from {}".format(self._dataset)).fetchall()[0][0]
            return _cursor.execute("SELECT {} FROM {}".format(list_of_variables, self._dataset))
        else:
            new_num_of_rows = _cursor.execute("SELECT count(1) from {}".format(self._dataset)).fetchall()[0][0]
            return _cursor.execute("""SELECT * FROM (
                SELECT {}, rowid as rowid FROM {} ORDER BY rowid DESC LIMIT {})
                ORDER BY rowid ASC;""".format(list_of_variables, self._dataset, new_num_of_rows - self._last_num_of_rows)
            )
