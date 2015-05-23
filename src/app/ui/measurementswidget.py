"""
RDB 2015

User Interface

Measurements Widget

Author: Tomas Krizek
"""

from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QVBoxLayout, QWidget

from filteringwidget import FilteringWidget
from paginatortablewidget import PaginatorTableWidget


class MeasurementsWidget(QWidget):

    requestData = pyqtSignal(dict, int, int)

    def __init__(self, parent=None):
        super(MeasurementsWidget, self).__init__(parent)

        self.offset = 0
        self.limit = 15
        self.filter = {}

        self.filteringWidget = FilteringWidget()
        self.filteringWidget.filterChanged.connect(self.on_filterChanged)

        self.table = PaginatorTableWidget()
        self.table.setPageRowCount(self.limit)
        self.table.requestData.connect(self.on_table_requestData)
        self.table.setColumnHeaders(['Datum a čas', 'Hodnota 1', 'Hodnota 2',
            'Rozdíl hodnot', 'Přístroj', 'Odchylka přístroje'])

        layout = QVBoxLayout()
        layout.addWidget(self.filteringWidget)
        layout.addWidget(self.table)
        self.setLayout(layout)

    @pyqtSlot(int, int)
    def on_table_requestData(self, offset, limit):
        self.offset = offset
        self.limit = limit
        self.requestData.emit(self.filter, self.offset, self.limit)

    @pyqtSlot(dict)
    def on_filterChanged(self, filter_):
        self.filter = filter_
        self.requestData.emit(self.filter, self.offset, self.limit)

    def setData(self, data):
        self.table.setData(data)

    def setMaxRowCount(self, rowCount):
        self.table.setMaxRowCount(rowCount)

    def setFilterOptions(self, options):
        self.filteringWidget.setOptions(options)

    def setFilter(self, filter_):
        self.filteringWidget.setFilter(filter_)


if __name__ == '__main__':

    import sys
    from PyQt5.QtWidgets import QApplication
    from datetime import datetime

    app = QApplication(sys.argv)

    options = {'block': [1, 2, 3, 4, 5], \
               'device': ['rm2-x', 'zc-3d', 'qap'], \
               'unit': ['Hz', 'A', 'm^2']}

    filter_ = {'block': 4, 'unit': 'Hz', 'deviated_values': True, \
               'start_datetime': datetime(2015,5,7,10)}

    widget = MeasurementsWidget()
    widget.setFilterOptions(options)
    widget.setFilter(filter_)
    widget.setMaxRowCount(100)

    @pyqtSlot(dict, int, int)
    def handle_requestData(filter_, offset, limit):
        print(filter_, offset, limit)

    widget.requestData.connect(handle_requestData)

    widget.setData([[1, 2, 3,4,5, 6], [3, 5, 6, 7, 8, 9]])
    widget.show()

    sys.exit(app.exec_())
