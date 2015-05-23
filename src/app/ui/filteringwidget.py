"""
RDB 2015

User Interface

Filtering Widget

Author: Tomas Krizek
"""


from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QPushButton, QLabel,
    QDialog)
from filtermeasurementswidget import FilterDialog
from copy import deepcopy
from datetime import timezone


class FilteringWidget(QWidget):

    filterChanged = pyqtSignal(dict)

    @staticmethod
    def filterToText(filter_):
        def appendText(original, additional):
            if not original:
                return additional
            return original + ', ' + additional

        if not filter_:
            return "(žádný)"

        text = ""

        if 'block' in filter_:
            text = appendText(text, 'Skupina měření: %s' % filter_['block'])
        if 'device' in filter_:
            text = appendText(text, 'Přístroj: %s' % filter_['device'])
        if 'unit' in filter_:
            text = appendText(text, 'Jednotka: %s' % filter_['unit'])
        if 'start_datetime' in filter_:
            text = appendText(text, 'Od: %s' % \
                utc_to_local(filter_['start_datetime']).
                strftime('%Y-%m-%d %H:%M:%S'))
        if 'end_datetime' in filter_:
            text = appendText(text, 'Do: %s' % \
                utc_to_local(filter_['end_datetime']).
                strftime('%Y-%m-%d %H:%M:%S'))
        if 'loc_x' in filter_:
            try:
                text = appendText(text, 'Lokace: (%s, %s, +-%s)' % 
                    (filter_['loc_x'], filter_['loc_y'], filter_['loc_tol']))
            except KeyError:
                pass
        if 'deviated_values' in filter_ and \
            filter_['deviated_values'] == True:
            text = appendText(text, 'Mimo odchylku')

        return text

    def __init__(self, parent=None):
        super(FilteringWidget, self).__init__(parent)

        self.filter = {}

        self.label = QLabel(self)
        self.label.setWordWrap(True)
        self.label.setText(FilteringWidget.filterToText(self.filter))

        self.changeFilter = QPushButton(self)
        self.changeFilter.setText("Upravit filtr")
        self.changeFilter.clicked.connect(self.on_changeFilter_clicked)

        self.removeFilter = QPushButton(self)
        self.removeFilter.setText("Smazat filtr")
        self.removeFilter.clicked.connect(self.on_removeFilter_clicked)

        layout = QHBoxLayout()
        layout.addWidget(QLabel("Aktivní filtr: "))
        layout.addWidget(self.label)
        layout.addStretch(1)
        layout.addWidget(self.changeFilter)
        layout.addWidget(self.removeFilter)
        self.setLayout(layout)

        self.setMinimumHeight(60)

    @pyqtSlot()
    def on_changeFilter_clicked(self):
        filterDialog = FilterDialog()
        filterDialog.initControls(options, self.filter)

        if filterDialog.exec_() == QDialog.Accepted:
            self.setFilter(filterDialog.filter())

    @pyqtSlot()
    def on_removeFilter_clicked(self):
        self.setFilter({})

    def setFilter(self, filter_):
        self.filter = filter_
        self.onFilterChange()

    def setOptions(self, options):
        self.options = options

    def onFilterChange(self):
        self.label.setText(FilteringWidget.filterToText(self.filter))


def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)


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

    widget = FilteringWidget()
    widget.setOptions(options)
    widget.setFilter(filter_)
    widget.show()

    sys.exit(app.exec_())

