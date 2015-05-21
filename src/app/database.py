"""
RDB 2015

Database Layer

Connection driver

Author: Tomas Krizek

"""

import psycopg2


REMOTE = {
    'host': '147.230.21.34',
    'database': 'RDB2015_DanielMadera',
    'user': 'student',
    'password': 'student'
}

LOCAL = {
    'host': '127.0.0.1',
    'database': 'RDB2015_DanielMadera',
    'user': 'postgres',
    'password': 'student'
}


def connect(location=REMOTE):
    """Opens and returns a database connection."""
    conn = psycopg2.connect(**location)
    with conn.cursor() as cur:
        cur.execute("set schema 'rdb'")
    return conn


def get_devices(conn):
    """Retrieves all devices from database."""
    sql = "select serial_number, description from devices"
    with conn.cursor() as cur:
        cur.execute(sql)
        return cur.fetchall()


def remove_device(conn, serial_number):
    sql = "delete from devices where serial_number = (%s)"
    with conn.cursor() as cur:
        cur.execute(sql, (serial_number,))
    conn.commit()


def get_blocks(conn):
    sql = "select id, description from blocks"
    with conn.cursor() as cur:
        cur.execute(sql)
        return cur.fetchall()


def remove_block(conn, id_):
    sql = "delete from blocks where id = (%s)"
    with conn.cursor() as cur:
        cur.execute(sql, (id_,))
    conn.commit()

