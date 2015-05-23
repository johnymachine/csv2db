"""
RDB 2015

UI-Database connection

Database Manager

Author: Tomas Krizek
"""

from PyQt5.QtCore import pyqtSlot, pyqtSignal, QThread, QMutex, QMutexLocker
import psycopg2
from datetime import datetime
import atexit


REMOTE = {
    'host': '147.230.21.34',
    'database': 'rdb2015_danielmadera',
    'user': 'student',
    'password': 'student'
}

LOCAL = {
    'host': '127.0.0.1',
    'database': 'rdb2015_danielmadera',
    'user': 'postgres',
    'password': 'student'
}


def connect(location=LOCAL):
    """Opens and returns a database connection."""
    conn = psycopg2.connect(**location)
    with conn.cursor() as cur:
        cur.execute("set schema 'rdb'")
    conn.commit()
    return conn


conMutex = QMutex()
conn = connect(LOCAL)
conMutex.unlock()


def get_devices():
    QMutexLocker(conMutex)
    """Retrieves all devices from database."""
    sql = 'select "serial_number", "description" from "devices"'
    with conn.cursor() as cur:
        cur.execute(sql)
        return cur.fetchall()


def remove_device(serial_number):
    QMutexLocker(conMutex)
    sql = 'delete from "devices" where "serial_number" = (%s)'
    with conn.cursor() as cur:
        cur.execute(sql, (serial_number,))
    conn.commit()


def get_blocks():
    QMutexLocker(conMutex)
    sql = 'select "id", "description" from "blocks"'
    with conn.cursor() as cur:
        cur.execute(sql)
        return cur.fetchall()


def remove_block(id_):
    QMutexLocker(conMutex)
    sql = 'delete from "blocks" where "id" = (%s)'
    with conn.cursor() as cur:
        cur.execute(sql, (id_,))
    conn.commit()


def import_data(data):
    """Performs multiple insert of data."""
    QMutexLocker(conMutex)
    sql = 'insert into rdb."raw_data_view"("created", "unit", "location_id", \
            "longitude", "latitude", "location_description", "value1", \
            "value2", "unit_deviation", "serial_number", "device_description", \
            "block_id", "block_description") values '

    with conn.cursor() as cur:
        args_str = ','.join(_get_import_values_string(cur, row) for row in data)
        cur.execute(sql + args_str)
    conn.commit()


def _get_import_values_string(cur, row):
    row[0] = datetime.utcfromtimestamp(int(row[0]))
    return cur.mogrify("(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
        row).decode('utf-8')


def export_data(filename):
    """Exports all raw_data."""
    QMutexLocker(conMutex)
    query = """
    select (select round(extract(epoch from "created" at time zone 'utc'))),\
            "unit", "location_id", \
            "longitude", "latitude", "location_description", "value1", \
            "value2", "unit_deviation", "serial_number", "device_description", \
            "block_id", "block_description"
    from rdb."raw_data_view"
    """

    outputquery = "COPY ({0}) TO STDOUT WITH CSV DELIMITER ';'".format(query)

    with conn.cursor() as cur:
        with open(filename, 'w') as f:
            cur.copy_expert(outputquery, f)




def execute(function, callback=None, *args, **kwargs):
    if callable(function):
        queue.append(
            {'function': function, \
             'callback': callback, \
             'args': args, \
             'kwargs': kwargs})
        _startExecution()


def _startExecution():
    if thread.done and queue:
        function = queue[0]['function']
        args = queue[0]['args']
        kwargs = queue[0]['kwargs']

        thread.execute(function, *args, **kwargs)


@pyqtSlot(dict)
def _on_thread_executed(dict_):
    callback = queue[0]['callback']
    del queue[0]
    
    _startExecution()

    if callable(callback):
        callback(dict_['returnValue'])


class FunctionThread(QThread):
    executed = pyqtSignal(dict)

    def __init__(self, parent=None):
        super(FunctionThread, self).__init__(parent)

        self.mutex = QMutex()
        
        self.function = None
        self.args = None
        self.kwargs = None
        self.returnValue = None

        self.finished.connect(self.on_thread_finished)

        self.done = True

    def __del__(self):
        self.wait()

    def execute(self, function, *args, **kwargs):
        locker = QMutexLocker(self.mutex)

        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.done = False

        self.start()

    def run(self):
        returnValue = self.function(*self.args, **self.kwargs)
        self.mutex.lock()
        self.returnValue = returnValue
        self.mutex.unlock()

    def on_thread_finished(self):
        result = {'returnValue': self.returnValue}
        self.done = True
        self.executed.emit(result)



@atexit.register
def unload_module():
    """Close db connection when module is unloaded."""
    conMutex.lock()
    conn.close()
    conMutex.unlock()


thread = FunctionThread()
queue = []

thread.executed.connect(_on_thread_executed)


if __name__ == "__main__":
    import sys
    from PyQt5.QtCore import QCoreApplication
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = QCoreApplication(sys.argv)
    print('before')
    execute(get_blocks, print)
    print('between')
    execute(get_devices, print)
    print('after')
    app.exec_()
