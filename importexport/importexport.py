#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import csv

class RdbDialect(csv.Dialect):
    #https://docs.python.org/3.5/library/csv.html#csv-fmt-params
    delimiter = ','
    doublequote = True
    escapechar = None
    lineterminator = "\r\n"
    quotechar = '"'
    quoting = csv.QUOTE_MINIMAL
    skipinitialspace = True
    strict = False


class RdbReader(object):

    def __init__(self, filename, dialect = RdbDialect, **kwds):
        self.file = open(filename, "r")
        self.reader = csv.reader(self.file, dialect=dialect, **kwds)

    def __enter__(self):
        return self

    def __iter__(self):
        return self

    def __next__(self):
        return self.reader.__next__()

    def readrow(self):
        return self.__next__()

    def readrows(self, rowscount = 1):
        rows = []
        for i in range(rowscount):
            rows.append(self.readrow())
        return rows

    def __exit__(self, *err):
        self.file.close()


class RdbWriter(object):

    def __init__(self, filename, dialect = RdbDialect, **kwds):
        self.file = open(filename, "w")
        self.writer = csv.writer(self.file, dialect=dialect, **kwds)

    def __enter__(self):
        return self

    def writerow(self, row):
        return self.writer.writerow(row)

    def writerows(self, rows):
        return self.writer.writerow([row for row in rows])

    def __exit__(self, *err):
        self.file.close()

if __name__ == "__main__":
    with RdbReader("in.csv") as rdbreader:
        row = rdbreader.readrows(1)
    with RdbWriter("out.csv") as rdbwriter:
        rows = row + row
        rdbwriter.writerows(rows)