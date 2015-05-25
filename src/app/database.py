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
import json


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
        cur.execute("set search_path to 'rdb'")
    conn.commit()
    return conn


with open("database.json", 'r') as stream:
	conn = connect(json.load(stream))


def get_devices():
    """Retrieves all devices from database."""
    sql = 'select "serial_number", "description" from "devices"'
    with conn.cursor() as cur:
        cur.execute(sql)
        return cur.fetchall()


def remove_device(serial_number):
    sql = 'delete from "devices" where "serial_number" = (%s)'
    with conn.cursor() as cur:
        cur.execute(sql, (serial_number,))
    conn.commit()


def get_blocks(filter_=None):
    sql = 'select "id", "description" from "blocks" where "id" in ({0}) order by "id"'
    subquery = 'select distinct "block_id" from "measurements_view"'
    with conn.cursor() as cur:
        cur.execute(sql.format(subquery + filter_to_sql(cur, filter_)))
        return cur.fetchall()


def remove_block(id_):
    sql = 'delete from "blocks" where "id" = (%s)'
    with conn.cursor() as cur:
        cur.execute(sql, (id_,))
    conn.commit()


def get_units():
    sql = 'select "unit" from "units"'
    with conn.cursor() as cur:
        cur.execute(sql)
        return cur.fetchall()


def get_measurements(filter_=None, offset=0, limit=20):
    sql_begin = 'select "created" at time zone \'utc\', "value1", "value2", "difference", \
            "device_description", "unit_deviation" from \
            "measurements_view"'
    with conn.cursor() as cur:
        sql = sql_begin + filter_to_sql(cur, filter_)
        sql = sql + cur.mogrify('order by "created" desc offset %s limit %s', 
            (offset, limit)).decode('utf-8')
        cur.execute(sql)
        return cur.fetchall()


def get_measurements_count(filter_=None, *args):
    sql = 'select count(1) from "measurements_view"'
    with conn.cursor() as cur:
        cur.execute(sql + filter_to_sql(cur, filter_))
        return cur.fetchone()[0]


def get_logs(filter_=None, offset=0, limit=20):
    sql_begin = 'select "created" at time zone \'utc\', "operation", "tablename", \
            "description" from "logs"'
    with conn.cursor() as cur:
        sql = sql_begin + filter_to_sql(cur, filter_)
        sql = sql + cur.mogrify('order by "created" desc offset %s limit %s', 
            (offset, limit)).decode('utf-8')
        cur.execute(sql)
        return cur.fetchall()


def filter_to_sql(cur, filter_):
    def join_conditions(original, additional, operator='and'):
        additional = ' ' + additional + ' '
        if not original:
            return additional
        return original + ' ' + operator + ' ' + additional

    if not filter_:
        return ''

    conditions = ''

    if 'operation' in filter_:
        additional = cur.mogrify('"operation" = %s', (filter_['operation'],)).decode('utf-8')
        conditions = join_conditions(conditions, additional)
    if 'tablename' in filter_:
        additional = cur.mogrify('"tablename" = %s', (filter_['tablename'],)).decode('utf-8')
        conditions = join_conditions(conditions, additional)
    if 'block' in filter_:
        additional = cur.mogrify('block_id = %s', (filter_['block'],)).decode('utf-8')
        conditions = join_conditions(conditions, additional)
    if 'device' in filter_:
        additional = cur.mogrify('serial_number = %s', (filter_['device'],)).decode('utf-8')
        conditions = join_conditions(conditions, additional)
    if 'unit' in filter_:
        additional = cur.mogrify('unit = %s', (filter_['unit'],)).decode('utf-8')
        conditions = join_conditions(conditions, additional)
    if 'start_datetime' in filter_ and 'end_datetime' in filter_:
        additional = cur.mogrify('created between %s and %s',
            (filter_['start_datetime'], filter_['end_datetime'],)).decode('utf-8')
        conditions = join_conditions(conditions, additional)
    if 'loc_x' in filter_ and 'loc_tol' in filter_:
        additional = cur.mogrify('loc_x between %s and %s',
            (float(filter_['loc_x']) - float(filter_['loc_tol']),
            float(filter_['loc_x']) + float(filter_['loc_tol']))).decode('utf-8')
        conditions = join_conditions(conditions, additional)
    if 'loc_y' in filter_ and 'loc_tol' in filter_:
        additional = cur.mogrify('loc_y between %s and %s',
            (float(filter_['loc_y']) - float(filter_['loc_tol']),
            float(filter_['loc_y']) + float(filter_['loc_tol']))).decode('utf-8')
        conditions = join_conditions(conditions, additional)
    if 'deviated_values' in filter_ and \
        filter_['deviated_values'] == True:
        additional = 'difference > unit_deviation'
        conditions = join_conditions(conditions, additional)

    return ' where ' + conditions


def import_data(data):
    """Performs multiple insert of data."""
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


def export_data(filename, filter_=None):
    """Exports all raw_data."""
    subquery = """
    select (select round(extract(epoch from "created" at time zone 'utc'))),\
            "unit", "location_id", \
            "longitude", "latitude", "location_description", "value1", \
            "value2", "unit_deviation", "serial_number", "device_description", \
            "block_id", "block_description"
    from rdb."raw_data_view"
    """
    query = "COPY ({0}) TO STDOUT WITH CSV DELIMITER ';'"

    with conn.cursor() as cur:
        subquery = subquery + filter_to_sql(cur, filter_)
        query = query.format(subquery)
        with open(filename, 'w') as f:
            cur.copy_expert(query, f)




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
    conn.close()


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
