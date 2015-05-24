"""
RDB 2015

User Interface

CustomTable Widget

Author: Tomas Krizek
"""

from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import (QTableWidget, QTableWidgetItem, QWidget,
    QAbstractItemView, QHeaderView)


class CustomTableWidget(QTableWidget):

    def __init__(self, parent=None):
        super(CustomTableWidget, self).__init__(parent)

        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setVisible(False)

    def setData(self, tableData):
        self.setRowCount(len(tableData))

        for i, rowData in enumerate(tableData):
            for j, columnData in enumerate(rowData):
                item = QTableWidgetItem(str(columnData))
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.setItem(i, j, item)

    def setColumnHeaders(self, columnHeaders):
        self.setColumnCount(len(columnHeaders))
        self.setHorizontalHeaderLabels(columnHeaders)
        self.horizontalHeader().setVisible(True)

    def getRowData(self, iRow):
        data = []
        for iCol in range(0, self.columnCount()):
            data.append(self.item(iRow, iCol).text())
        return tuple(data)
