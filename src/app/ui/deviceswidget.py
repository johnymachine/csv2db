"""
RDB 2015

User Interface

View Remove Table Widget for devices, blocks of measurements

Author: Tomas Krizek
"""

from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import (QTableWidget, QWidget,
    QVBoxLayout, QPushButton, QAbstractItemView, QLabel)

from customtablewidget import CustomTableWidget


class DevicesWidget(QWidget):

    removeRow = pyqtSignal(int)

    def __init__(self, parent=None):
        super(DevicesWidget, self).__init__(parent)

        self.label = QLabel(self)
        self.table = CustomTableWidget(self)
        self.button = QPushButton(self)
        self.button.clicked.connect(self.on_button_clicked)

        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)

        self.button.setText("Odstranit přístroj")

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.table)
        layout.addWidget(self.button)
        self.setLayout(layout)

    def setData(self, tableData):
        self.table.setData(tableData)

    def setColumnHeaders(self, columnHeaders):
        self.table.setColumnHeaders(columnHeaders)

    def getRowData(self, iRow):
        self.table.getRowData(iRow)

    @pyqtSlot()
    def on_button_clicked(self):
        selected = self.table.selectionModel().selectedRows()
        if selected:
            self.removeRow.emit(selected[0].row())


if __name__ == '__main__':

    import sys
    from PyQt5.QtWidgets import QApplication, QMessageBox

    app = QApplication(sys.argv)

    widget = DevicesWidget()
    widget.setColumnHeaders(["Name", "Hair Color"])
    widget.show()

    tableData = [
        ("Alice", 'aliceblue'),
        ("Neptun", 'aquamarine'),
        ("Ferdinand", 'springgreen')
    ]
    widget.setData(tableData)

    @pyqtSlot(int)
    def on_widget_removeRow(index):
        msgBox = QMessageBox()
        msgBox.setText(str(index))
        msgBox.exec_()

    widget.removeRow.connect(on_widget_removeRow)

    sys.exit(app.exec_())
