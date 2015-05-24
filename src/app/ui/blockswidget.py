"""
RDB 2015

User Interface

Blocks Widget

Author: Tomas Krizek
"""

from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import (QTableWidget, QWidget,
    QVBoxLayout, QPushButton, QAbstractItemView, QLabel)

from .filteringwidget import FilteringWidget
from .customtablewidget import CustomTableWidget


class BlocksWidget(QWidget):

    removeBlock = pyqtSignal(int)
    requestData = pyqtSignal(dict)
    requestDetail = pyqtSignal(int)

    def __init__(self, parent=None):
        super(BlocksWidget, self).__init__(parent)

        self._filter = {}

        self.filtering = FilteringWidget()
        self.filtering.filterChanged.connect(self.on_filterChanged)

        self.table = CustomTableWidget()
        self.table.setColumnHeaders(['Číslo skupiny', 'Popis'])
        self.table.cellDoubleClicked.connect(self.on_table_doubleClick)
        self.table.horizontalHeader().resizeSection(0, 160)

        self.button = QPushButton(self)
        self.button.clicked.connect(self.on_button_clicked)
        self.button.setText("Odstranit blok měření")

        layout = QVBoxLayout()
        layout.addWidget(self.filtering)
        layout.addWidget(self.table)
        layout.addWidget(self.button)
        self.setLayout(layout)

    def setData(self, tableData):
        self.table.setData(tableData)

    @pyqtSlot()
    def on_button_clicked(self):
        selected = self.table.selectionModel().selectedRows()
        if selected:
            self.removeBlock.emit(int(selected[0].data()))

    @pyqtSlot(dict)
    def on_filterChanged(self, filter_):
        self._filter = filter_
        self.updateData()

    def setFilterOptions(self, options):
        self.filtering.setOptions(options)

    def setFilter(self, filter_):
        self.filtering.setFilter(filter_)

    @pyqtSlot(int, int)
    def on_table_doubleClick(self, iRow, iCol):
        self.requestDetail.emit(int(self.table.item(iRow, 0).text()))

    def filter(self):
        return self._filter

    def updateData(self):
        self.requestData.emit(self._filter)


if __name__ == '__main__':

    import sys
    from PyQt5.QtWidgets import QApplication, QMessageBox
    from datetime import datetime

    app = QApplication(sys.argv)

    options = {'block': [1, 2, 3, 4, 5], \
               'device': ['rm2-x', 'zc-3d', 'qap'], \
               'unit': ['Hz', 'A', 'm^2']}

    filter_ = {'block': 4, 'unit': 'Hz', 'deviated_values': True, \
               'start_datetime': datetime(2015,5,7,10)}

    widget = BlocksWidget()
    widget.setFilterOptions(options)
    widget.setFilter(filter_)
    widget.setData([[1, 'Skupina'], [2, 'Skds']])

    @pyqtSlot(dict)
    def handle_requestData(filter_):
        print(filter_)

    @pyqtSlot(int)
    def on_widget_removeBlock(index):
        msgBox = QMessageBox()
        msgBox.setText("remove: " + str(index))
        msgBox.exec_()

    @pyqtSlot(int)
    def on_widget_requestDetail(index):
        msgBox = QMessageBox()
        msgBox.setText("detail: " + str(index))
        msgBox.exec_()

    widget.removeBlock.connect(on_widget_removeBlock)
    widget.requestData.connect(handle_requestData)
    widget.requestDetail.connect(on_widget_requestDetail)
    widget.show()

    sys.exit(app.exec_())
