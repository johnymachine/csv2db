"""
Main application window.

Author: Tomas Krizek
"""

from PyQt5.QtWidgets import QMainWindow, qApp, QMessageBox, QFileDialog
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSlot
from copy import deepcopy

from .. import database as db
from .importdialog import ImportDialog
from .deviceswidget import DevicesWidget
from .blockswidget import BlocksWidget
from .measurementswidget import MeasurementsWidget


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.options = {}
        self.setupUi(self)
        self.updateData()

        self.on_requestBlockData(self.blocksWidget.filter())
        self.on_requestMeasurementData(self.measurementsWidget.filter(), 
            self.measurementsWidget.offset, self.measurementsWidget.limit)

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)

        # TABS
        self.tabsWidget = QtWidgets.QTabWidget(MainWindow)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabsWidget.sizePolicy().
            hasHeightForWidth())
        self.tabsWidget.setSizePolicy(sizePolicy)

        self.devicesWidget = DevicesWidget()
        self.devicesWidget.removeDevice.connect(self.on_removeDevice)

        self.blocksWidget = BlocksWidget()
        self.blocksWidget.removeBlock.connect(self.on_removeBlock)
        self.blocksWidget.requestData.connect(self.on_requestBlockData)
        self.blocksWidget.requestDetail.connect(self.on_requestBlockDetail)

        self.measurementsWidget = MeasurementsWidget()
        self.measurementsWidget.requestData.connect(self.on_requestMeasurementData)

        self.tabsWidget.addTab(self.blocksWidget, "Skupiny měření")
        self.tabsWidget.addTab(self.measurementsWidget, "Naměřené hodnoty")
        self.tabsWidget.addTab(self.devicesWidget, "Přístroje")

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

    def setDevices(self, devices):
        if devices:
            self.devicesWidget.setData(devices)
            self.options['device'] = [device[0] for device in devices]
            self.on_options_updated()

    @pyqtSlot(str)
    def on_removeDevice(self, serial_number):
        title = "Odstranit přístroj %s?" % serial_number
        text = "Odstraněním přístroje se smažou i všechny jím naměřené " + \
                "hodnoty.\n\nOpravdu chcete odstranit přístroj %s?" % \
                serial_number
        buttons = QMessageBox.Yes | QMessageBox.No
        msgBox = QMessageBox(QMessageBox.Question, title, text, buttons)
        
        if msgBox.exec_() == QMessageBox.Yes:
            db.execute(db.remove_device, self.updateData, serial_number)

    def setBlocks(self, blocks):
        if blocks:
            self.options['block'] = [block[0] for block in blocks]
            self.on_options_updated()

    @pyqtSlot(int)
    def on_removeBlock(self, block_id):
        title = "Odstranit měřící blok %s?" % block_id
        text = "Odstraněním měřícího bloku se smažou i všechny naměřené " + \
                "hodnoty v rámci tohoto bloku.\n\nOpravdu chcete " + \
                "odstranit měřící blok %s?" % block_id
        buttons = QMessageBox.Yes | QMessageBox.No
        msgBox = QMessageBox(QMessageBox.Question, title, text, buttons)
        
        if msgBox.exec_() == QMessageBox.Yes:
            db.execute(db.remove_block, self.on_blockRemoved, block_id)

    def on_blockRemoved(self, *args):
        db.execute(db.get_blocks, self.setBlocks)
        self.blocksWidget.updateData()

    @pyqtSlot(dict)
    def on_requestBlockData(self, filter_):
        db.execute(db.get_blocks, self.blocksWidget.setData, filter_)
        #TODO test

    @pyqtSlot(int)
    def on_requestBlockDetail(self, block_id):
        filter_ = deepcopy(self.blocksWidget.filter())
        filter_['block'] = block_id
        self.measurementsWidget.setFilter(filter_)
        self.tabsWidget.setCurrentIndex(1)

    def on_action_Import_triggered(self):
        caption = 'Import csv dat'
        dialog = QFileDialog(self, caption)
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setNameFilters(['CSV soubory (*.csv)', 'Všechny soubory (*)'])
        if dialog.exec_():
            importDialog = ImportDialog()
            importDialog.setFilename(dialog.selectedFiles()[0])
            importDialog.exec_()
            self.updateData()

    def on_action_Export_triggered(self):
        caption = 'Export dat do csv'
        dialog = QFileDialog(self, caption)
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setAcceptMode(QFileDialog.AcceptSave)
        dialog.setNameFilter('CSV soubory (*.csv)')
        dialog.setDefaultSuffix('csv')
        if dialog.exec_():
            filename = dialog.selectedFiles()[0]
            # TODO
            # db.export_data(self.conn, filename)

    def updateData(self, *args):
        db.execute(db.get_blocks, self.setBlocks)
        db.execute(db.get_devices, self.setDevices)
        db.execute(db.get_units, self.setUnits)

    def setUnits(self, units):
        if units:
            self.options['unit'] = [unit[0] for unit in units]
            self.on_options_updated()

    def on_options_updated(self):
        self.blocksWidget.setFilterOptions(self.options)
        self.measurementsWidget.setFilterOptions(self.options)

    @pyqtSlot(dict, int, int)
    def on_requestMeasurementData(self, filter_, offset, limit):
        # db.execute(db.get_measurements_count,
        #     self.measurementsWidget.setMaxRowCount,
        #     filter_)
        db.execute(db.get_measurements,
            self.measurementsWidget.setData,
            filter_, offset, limit)

