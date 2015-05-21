"""
RDB 2015

TEST Database Layer

Author: Tomas Krizek

"""

import unittest

from .database import *


class TestDatabase(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestDatabase, self).__init__(*args, **kwargs)
        self.conn = connect(LOCAL)

    def __del__(self):
        self.conn.close()

    def test_connection(self):
        with self.conn.cursor() as cur:
            cur.execute('select 1')
            result = cur.fetchone()
            assert result[0] == 1

    def test_get_devices(self):
        devs = devices.get_devices(self.conn)
        self.assertEquals(len(devs), 4)
        print(devs)
