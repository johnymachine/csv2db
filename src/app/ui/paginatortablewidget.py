"""
RDB 2015

User Interface

Paginator Table Widget

Author: Tomas Krizek
"""

from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import (QTableWidget, QTableWidgetItem, QWidget,
    QVBoxLayout, QAbstractItemView, QMessageBox)
from math import ceil
import sys

from .paginationcontrols import PaginationControls
from .customtablewidget import CustomTableWidget


class PaginatorTableWidget(QWidget):
    PAGE_ROW_COUNT = 13

    requestData = pyqtSignal(int, int)

    def __init__(self, parent=None):
        super(PaginatorTableWidget, self).__init__(parent)

        self.table = CustomTableWidget(self)
        self.controls = PaginationControls(self)
        self.controls.startButton.setVisible(False)
        self.controls.endButton.setVisible(False)
        self.controls.setMaximum(1000000000)

        # self._maxRowCount = 0
        self._pageRowCount = PaginatorTableWidget.PAGE_ROW_COUNT

        self.createGUI()

    def createGUI(self):
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)

        self.controls.valueChanged.connect(self.on_controls_valueChanged)

        layout = QVBoxLayout(self)
        layout.addWidget(self.table)
        layout.addWidget(self.controls)
        self.setLayout(layout)

    # def maxRowCount(self):
    #     return self._maxRowCount

    # def setMaxRowCount(self, value):
    #     if value >= 0:
    #         self._maxRowCount = value
    #     self._updatePaginationControls()

    def pageRowCount(self):
        return self._pageRowCount

    def setPageRowCount(self, value):
        if value > 0:
            self._pageRowCount = value
        # self._updatePaginationControls()

    # def _updatePaginationControls(self):
    #     maximum = ceil(self._maxRowCount / self._pageRowCount)
    #     if maximum == 0:
    #         maximum = 1
    #     self.controls.setMaximum(maximum)

    @pyqtSlot(int)
    def on_controls_valueChanged(self, value):
        offset = (value - 1) * self._pageRowCount
        limit = self._pageRowCount
        self.requestData.emit(offset, limit)

    def setData(self, data):
        self.table.setData(data)

    def setColumnHeaders(self, columnHeaders):
        self.table.setColumnHeaders(columnHeaders)

    # def resizeEvent(self, event):
    #     rowHeight = self.table.visualItemRect(self.table.item(0, 0)).height() + 2
    #     rowViewPortHeight = self.table.height()
    #     self.setPageRowCount(int(rowViewPortHeight / rowHeight))
    #     self.on_controls_valueChanged(self.controls.counter.value())


if __name__ == '__main__':

    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)

    widget = PaginatorTableWidget()
    widget.setMaxRowCount(23)
    widget.setPageRowCount(7)
    widget.show()

    sys.exit(app.exec_())

