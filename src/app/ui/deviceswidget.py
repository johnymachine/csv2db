"""
RDB 2015

User Interface

Devices Widget

Author: Tomas Krizek
"""

from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import (QTableWidget, QWidget,
    QVBoxLayout, QPushButton, QAbstractItemView, QLabel)

from customtablewidget import CustomTableWidget


class DevicesWidget(QWidget):

    removeDevice = pyqtSignal(str)

    def __init__(self, parent=None):
        super(DevicesWidget, self).__init__(parent)

        self.table = CustomTableWidget(self)
        self.table.setColumnHeaders(['Sériové číslo', 'Popis'])

        self.button = QPushButton(self)
        self.button.clicked.connect(self.on_button_clicked)
        self.button.setText("Odstranit přístroj")

        layout = QVBoxLayout()
        layout.addWidget(self.table)
        layout.addWidget(self.button)
        self.setLayout(layout)

    def setData(self, tableData):
        self.table.setData(tableData)

    def getRowData(self, iRow):
        self.table.getRowData(iRow)

    @pyqtSlot()
    def on_button_clicked(self):
        selected = self.table.selectionModel().selectedRows()
        if selected:
            self.removeDevice.emit(selected[0].data())


if __name__ == '__main__':

    import sys
    from PyQt5.QtWidgets import QApplication, QMessageBox

    app = QApplication(sys.argv)

    widget = DevicesWidget()
    widget.show()

    tableData = [
        ("qap-3", 'aliceblue'),
        ("bfg-1", 'aquamarine'),
        ("topkek9", 'springgreen')
    ]
    widget.setData(tableData)

    @pyqtSlot(int)
    def on_widget_removeRow(serial):
        msgBox = QMessageBox()
        msgBox.setText(serial)
        msgBox.exec_()

    widget.removeDevice.connect(on_widget_removeRow)

    sys.exit(app.exec_())
