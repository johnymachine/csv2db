#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import csv

class CsvDialect(csv.Dialect):
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


class CsvReader(object):
    ROWS_CHUNK = 1000

    def __init__(self, filename, dialect, **kwds):
        self.file = open(filename, "r")
        self.reader = csv.reader(self.file, dialect=dialect, **kwds)

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

    def readrows(self, rows_chunk=ROWS_CHUNK):
        rows = []
        for i in range(rows_chunk):  # read a chunk of rows
            try:
                rows.append(self.readrow())
            except StopIteration:  # end of file
                break
        return rows
            
    def close(self):
        self.file.close()


if __name__ == "__main__":
    csvreader = CsvReader("in.csv", RdbCsvDialect)
    for rows in csvreader.readall(998):
        print(len(rows))
    csvreader.close()