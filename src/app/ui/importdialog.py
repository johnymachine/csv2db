"""
RDB 2015

User Interface

Import Process Dialog

Author: Tomas Krizek
"""

from PyQt5.QtCore import Qt, QTimer, pyqtSlot
from PyQt5.QtWidgets import (QApplication, QDialog, QGridLayout, QLabel)
import time
from .. import database as db
from ..csv import CsvReader, CsvDialect


class ImportDialog(QDialog):
    def __init__(self, parent=None):
        super(ImportDialog, self).__init__(parent)

        self.cancelled = False
        self.requestCancel = False

        self.rowsChunk = 20000 #CsvReader.ROWS_CHUNK

        self.rowCount = 0
        self.timeStart = time.time()

        self.timer = QTimer()
        self.timer.timeout.connect(self.updateProcessed)
        self.timer.start(500)

        label = QLabel("Probíhá zpracování, prosím čekejte.")
        
        self.labelRows = QLabel("0")
        self.labelSpeed = QLabel("0")

        mainLayout = QGridLayout()
        mainLayout.addWidget(label, 0, 0, 1, 2)
        mainLayout.addWidget(QLabel("Zpracováno řádků: "), 1, 0)
        mainLayout.addWidget(self.labelRows, 1, 1)
        mainLayout.addWidget(QLabel("Rychlost zpracování: "), 2, 0)
        mainLayout.addWidget(self.labelSpeed, 2, 1)
        self.setLayout(mainLayout)

        self.setWindowTitle("Import")
        self.setModal(True)

    @pyqtSlot()
    def updateProcessed(self):
        self.labelRows.setText(str(self.rowCount))
        rowsPerSecond = self.rowCount / (time.time() - self.timeStart)
        self.labelSpeed.setText("%d" % rowsPerSecond)

    def setFilename(self, filename):
        self.filename = filename

    def showEvent(self, event):
        super(ImportDialog, self).showEvent(event)

        self.csvReader = CsvReader(self.filename, CsvDialect)
        self.timeStart = time.time()
        
        def afterInsert(*args):
            self.rowCount = self.rowCount + self.rowsChunk
            if self.requestCancel:
                self.cancelled = True
                self.reject()
            else:
                data = self.csvReader.readrows(self.rowsChunk)
                if not data:
                    self.accept()
                else:
                    db.execute(db.import_data, afterInsert, data)
        
        data = self.csvReader.readrows(self.rowsChunk)
        db.execute(db.import_data, afterInsert, data)

    def closeEvent(self, event):
        self.requestCancel = True
        if not self.cancelled:
            event.ignore()
        else:
            event.accept()


if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    dialog = ImportDialog()
    dialog.show()

    # @pyqtSlot()
    # def update():
    #     dialog.rowsLoaded(500)

    # timer = QTimer()
    # timer.timeout.connect(update)
    # timer.start(200)

    sys.exit(app.exec_())

