#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import csv

class RdbCsvDialect(csv.Dialect):
    # https://docs.python.org/3.5/library/csv.html#csv-fmt-params
    # default values
    delimiter = ';'
    doublequote = False
    escapechar = None
    lineterminator = "\r\n"
    quotechar = '"'
    quoting = csv.QUOTE_MINIMAL
    skipinitialspace = True
    strict = True


class RdbCsvReader(object):

    ROWS_CHUNK = 1000

    def __init__(self, filename, dialect, **kwds):
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

    def readall(self, rows_chunk=ROWS_CHUNK):
        reading_complete = False
        while not reading_complete:  # read file while possible
            rows = []
            for i in range(rows_chunk):  # read a chunk of rows
                try:
                    rows.append(self.readrow())
                except StopIteration:  # end of file
                    reading_complete = True
                    break
            if not rows:  # don't yield an empty list at the end of file
                return
            yield rows
            
    def __exit__(self, *err):
        self.file.close()


class RdbCsvWriter(object):

    def __init__(self, filename, dialect, **kwds):
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
    rows = []

    with RdbCsvReader("in.csv", RdbCsvDialect) as csvreader:
        for rows in csvreader.readall(998):
            print(len(rows))

    with RdbCsvWriter("out.csv", RdbCsvDialect) as csvwriter:
        csvwriter.writerows(rows)