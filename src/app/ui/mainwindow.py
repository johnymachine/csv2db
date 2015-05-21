"""
Main application window.

Author: Tomas Krizek
"""

from PyQt5.QtWidgets import QMainWindow, qApp, QMessageBox
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSlot

from .. import database as db
from .viewremovetablewidget import ViewRemoveTableWidget


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.conn = db.connect(db.LOCAL)
        self.setupUi(self)

        self.populateDevices()

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)

        self.tabsWidget = QtWidgets.QTabWidget(MainWindow)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabsWidget.sizePolicy().hasHeightForWidth())
        self.tabsWidget.setSizePolicy(sizePolicy)

        self.devicesWidget = ViewRemoveTableWidget(self.tabsWidget)
        self.devicesWidget.setColumnHeaders(['Sériové číslo', 'Název'])
        self.devicesWidget.removeRow.connect(self.on_devicesWidget_removeRow)
        self.devicesWidget.button.setText('Odstranit přístroj')
        self.tabsWidget.addTab(self.devicesWidget, "Přístroje")

        self.setCentralWidget(self.tabsWidget)

        # QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def populateDevices(self):
        self.devicesWidget.setData(db.get_devices(self.conn))

    @pyqtSlot(str)
    def on_devicesWidget_removeRow(self, id_):
        title = "Odstranit přístroj %s?" % id_
        text = "Odstraněním přístroje se smažou i všechny jím naměřené \
                hodnoty.\n\nOpravdu chcete odstranit přístroj %s?" % id_
        buttons = QMessageBox.Yes | QMessageBox.No
        msgBox = QMessageBox(QMessageBox.Question, title, text, buttons)
        
        if msgBox.exec_() == QMessageBox.Yes:
            db.remove_device(self.conn, id_)
            self.populateDevices()
  

    def __del__(self):
        del self.conn

    def _uconvert(self, text):
        """Converts QString encoding to Python unicode string."""
        return unicode(self.text_codec.fromUnicode(text), 'UTF-16')
