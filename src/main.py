"""
Main - application start point.

Author: Tomas Krizek
"""

import sys
from PyQt5.QtWidgets import QApplication


def main():
    from app import MainWindow

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


def main_dev():
    from PyQt5.QtCore import pyqtSlot
    from PyQt5.QtWidgets import QMessageBox
    from app.ui.viewremovetablewidget import ViewRemoveTableWidget
    from app import database as db

    app = QApplication(sys.argv)

    widget = ViewRemoveTableWidget()
    widget.show()

    conn = db.connect(db.LOCAL)
    tableData = db.get_devices(conn)
    columnHeaders = ["Serial Number", "Description"]

    widget.setData(tableData, columnHeaders)

    @pyqtSlot(str)
    def on_widget_removeRow(id_):
        msgBox = QMessageBox()
        msgBox.setText(id_)
        msgBox.exec_()

    widget.removeRow.connect(on_widget_removeRow)

    conn.close()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()