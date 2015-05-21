"""
Main application window.

Author: Tomas Krizek
"""

from PyQt5.QtWidgets import QMainWindow, qApp, QMessageBox, QFileDialog
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSlot

from .. import database as db
from ..csv import CsvReader, CsvDialect
from .viewremovetablewidget import ViewRemoveTableWidget


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.conn = db.connect(db.LOCAL)
        self.setupUi(self)

        self.populateDevices()
        self.populateBlocks()

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)

        # TABS
        self.tabsWidget = QtWidgets.QTabWidget(MainWindow)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabsWidget.sizePolicy().hasHeightForWidth())
        self.tabsWidget.setSizePolicy(sizePolicy)

        # DEVICES
        self.devicesWidget = ViewRemoveTableWidget(self.tabsWidget)
        self.devicesWidget.setColumnHeaders(['Sériové číslo', 'Název'])
        self.devicesWidget.removeRow.connect(self.on_devicesWidget_removeRow)
        self.devicesWidget.button.setText('Odstranit přístroj')
        self.devicesWidget.label.setText('Přístroje')

        # BLOCKS
        self.blocksWidget = ViewRemoveTableWidget(self.tabsWidget)
        self.blocksWidget.setColumnHeaders(['Identifikátor', 'Název'])
        self.blocksWidget.removeRow.connect(self.on_blocksWidget_removeRow)
        self.blocksWidget.button.setText('Odstranit měřící blok')
        self.blocksWidget.label.setText('Měřící bloky')

        widget = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.devicesWidget)
        layout.addWidget(self.blocksWidget)
        widget.setLayout(layout)
        self.tabsWidget.addTab(widget, "Přístroje a měřící bloky")

        self.setCentralWidget(self.tabsWidget)

        # MENU
        menuBar = QtWidgets.QMenuBar(MainWindow)
        menuBar.setGeometry(QtCore.QRect(0, 0, 800, 20))

        action_Import = QtWidgets.QAction(MainWindow)
        action_Import.setText('&Import')
        action_Import.triggered.connect(self.on_action_Import_triggered)
        action_Export = QtWidgets.QAction(MainWindow)
        action_Export.setText('&Export')
        action_Export.triggered.connect(self.on_action_Export_triggered)

        menu_File = QtWidgets.QMenu(menuBar)
        menu_File.setTitle('&Soubor')
        menu_File.addAction(action_Import)
        menu_File.addAction(action_Export)
        menuBar.addAction(menu_File.menuAction())

        menu_About = QtWidgets.QMenu(menuBar)
        menu_About.setTitle('O &aplikaci')
        menuBar.addAction(menu_About.menuAction())
        
        MainWindow.setMenuBar(menuBar)

    def populateDevices(self):
        self.devicesWidget.setData(db.get_devices(self.conn))

    @pyqtSlot(int)
    def on_devicesWidget_removeRow(self, iRow):
        data = self.devicesWidget.getRowData(iRow)
        serial_number = data[0]
        description = data[1]
        title = "Odstranit přístroj %s (%s)?" % (description, serial_number)
        text = "Odstraněním přístroje se smažou i všechny jím naměřené " + \
                "hodnoty.\n\nOpravdu chcete odstranit přístroj %s (%s)?" % \
                (description, serial_number)
        buttons = QMessageBox.Yes | QMessageBox.No
        msgBox = QMessageBox(QMessageBox.Question, title, text, buttons)
        
        if msgBox.exec_() == QMessageBox.Yes:
            db.remove_device(self.conn, serial_number)
            self.populateDevices()
  
    def populateBlocks(self):
        self.blocksWidget.setData(db.get_blocks(self.conn))

    @pyqtSlot(int)
    def on_blocksWidget_removeRow(self, iRow):
        data = self.blocksWidget.getRowData(iRow)
        id_ = data[0]
        description = data[1]
        title = "Odstranit měřící blok %s (%s)?" % (description, id_)
        text = "Odstraněním měřícího bloku se smažou i všechny naměřené " + \
                "hodnoty v rámci tohoto bloku.\n\nOpravdu chcete " + \
                "odstranit měřící blok %s (%s)?" % (description, id_)
        buttons = QMessageBox.Yes | QMessageBox.No
        msgBox = QMessageBox(QMessageBox.Question, title, text, buttons)
        
        if msgBox.exec_() == QMessageBox.Yes:
            db.remove_block(self.conn, id_)
            self.populateBlocks()

    def on_action_Import_triggered(self):
        caption = 'Import csv dat'
        dialog = QFileDialog(self, caption)
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setNameFilters(['CSV soubory (*.csv)', 'Všechny soubory (*)'])
        if dialog.exec_():
            filename = dialog.selectedFiles()[0]
            filename = '/home/sharp/drive/tul/n1-l/rdb/csv2db/testdata/in.csv'
            # TODO progress bar, exception handling
            with CsvReader(filename, CsvDialect) as csvreader:
                for rows in csvreader.readall():
                    db.import_data(self.conn, rows)

    def on_action_Export_triggered(self):
        print('export')

    def __del__(self):
        del self.conn

    def _uconvert(self, text):
        """Converts QString encoding to Python unicode string."""
        return unicode(self.text_codec.fromUnicode(text), 'UTF-16')
