"""
RDB 2015

User Interface

View Remove Table Widget for devices, blocks of measurements

Author: Tomas Krizek

"""


from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import (QTableWidget, QTableWidgetItem, QWidget,
    QVBoxLayout, QPushButton, QAbstractItemView, QMessageBox)


class ViewRemoveTableWidget(QWidget):

    removeRow = pyqtSignal(str)

    def __init__(self, parent=None):
        super(ViewRemoveTableWidget, self).__init__(parent)

        self.idColumnIndex = 0

        self.table = QTableWidget(self)

        self.button = QPushButton(self)
        self.button.clicked.connect(self.on_button_clicked)

        self.createGUI()

    def createGUI(self):
        self.button.setText("Odstranit řádek")

        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)

        layout = QVBoxLayout()
        layout.addWidget(self.table)
        layout.addWidget(self.button)
        self.setLayout(layout)

    def setData(self, tableData):
        self.table.setRowCount(len(tableData))

        for i, rowData in enumerate(tableData):
            for j, columnData in enumerate(rowData):
                item = QTableWidgetItem(columnData)
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.table.setItem(i, j, item)

        self.table.resizeColumnToContents(0)

    def setColumnHeaders(self, columnHeaders):
        self.table.setColumnCount(len(columnHeaders))
        self.table.setHorizontalHeaderLabels(columnHeaders)
        self.table.horizontalHeader().setVisible(True)

    def setIdColumnIndex(self, columnIndex=0):
        """Sets the index of column which contains the identifier of row."""
        self.idColumnIndex = columnIndex

    @pyqtSlot()
    def on_button_clicked(self):
        selected = self.table.selectionModel().selectedRows()
        if selected:
            row = selected[0].row()
            column = self.idColumnIndex
            id_ = self.table.item(row, column).text()
            self.removeRow.emit(id_)


if __name__ == '__main__':

    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)

    widget = ViewRemoveTableWidget()
    widget.setColumnHeaders(["Name", "Hair Color"])
    widget.show()

    tableData = [
        ("Alice", 'aliceblue'),
        ("Neptun", 'aquamarine'),
        ("Ferdinand", 'springgreen')
    ]
    widget.setData(tableData, columnHeaders)

    @pyqtSlot(str)
    def on_widget_removeRow(id_):
        msgBox = QMessageBox()
        msgBox.setText(id_)
        msgBox.exec_()

    widget.removeRow.connect(on_widget_removeRow)

    sys.exit(app.exec_())
