"""
RDB 2015

User Interface

Log Widget

Author: Tomas Krizek
"""


from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QTimeZone, QDateTime
from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QPushButton, QLabel,
    QDialog, QVBoxLayout, QComboBox, QDateTimeEdit, QFormLayout, QHBoxLayout)
from datetime import datetime, timezone
import calendar

from .filteringwidget import FilteringWidget
from .paginatortablewidget import PaginatorTableWidget


class LogsWidget(QWidget):

    requestData = pyqtSignal(dict, int, int)

    def __init__(self, parent=None):
        super(LogsWidget, self).__init__(parent)

        self.offset = 0
        self.limit = PaginatorTableWidget.PAGE_ROW_COUNT
        self._filter = {}

        self.filtering = LogFilteringWidget()
        self.filtering.filterChanged.connect(self.on_filterChanged)

        self.table = PaginatorTableWidget()
        self.table.layout().setContentsMargins(0, 0, 0, 0)
        self.table.setPageRowCount(self.limit)
        self.table.requestData.connect(self.on_table_requestData)
        self.table.setColumnHeaders(['Datum a čas', 'Operace',
            'Tabulka', 'Popis'])
        header = self.table.table.horizontalHeader()
        header.resizeSection(0, 190)
        header.resizeSection(1, 110)
        header.resizeSection(2, 110)
        header.resizeSection(3, 110)

        layout = QVBoxLayout()
        layout.addWidget(self.filtering)
        layout.addWidget(self.table)
        self.setLayout(layout)

    @pyqtSlot(int, int)
    def on_table_requestData(self, offset, limit):
        self.offset = offset
        self.limit = limit
        self.requestData.emit(self._filter, self.offset, self.limit)

    @pyqtSlot(dict)
    def on_filterChanged(self, filter_):
        self._filter = filter_
        self.table.controls.counter.setValue(1)
        self.requestData.emit(self._filter, self.offset, self.limit)

    def setData(self, data):
        self.table.setData(data)

    def setMaxRowCount(self, rowCount):
        self.table.setMaxRowCount(rowCount)

    def setFilterOptions(self, options):
        self.filtering.setOptions(options)

    def setFilter(self, filter_):
        self.filtering.setFilter(filter_)

    def filter(self):
        return self._filter

    def updateData(self):
        self.requestData.emit(self._filter, self.offset, self.limit)


class LogFilteringWidget(FilteringWidget):

    @staticmethod
    def filterToText(filter_):
        def appendText(original, additional):
            if not original:
                return additional
            return original + ', ' + additional

        if not filter_:
            return "(žádný)"

        text = ""

        if 'operation' in filter_:
            text = appendText(text, 'Operace: %s' % filter_['operation'])
        if 'tablename' in filter_:
            text = appendText(text, 'Tabulka: %s' % filter_['tablename'])
        if 'start_datetime' in filter_:
            text = appendText(text, 'Od: %s' % \
                utc_to_local(filter_['start_datetime']).
                strftime('%Y-%m-%d %H:%M:%S'))
        if 'end_datetime' in filter_:
            text = appendText(text, 'Do: %s' % \
                utc_to_local(filter_['end_datetime']).
                strftime('%Y-%m-%d %H:%M:%S'))

        return text

    @pyqtSlot()
    def on_changeFilter_clicked(self):
        pass
        filterDialog = LogFilterDialog()
        filterDialog.initControls(self._filter)

        if filterDialog.exec_() == QDialog.Accepted:
            self.setFilter(filterDialog.filter())


TZ = QTimeZone('Europe/Prague')


class LogFilterDialog(QDialog):
    OPERATION_OPTIONS = ['', 'insert', 'delete']
    TABLENAME_OPTIONS = ['', 'blocks', 'devices', 'measurements',\
                        'raw_data_view']

    def __init__(self, parent=None):
        super(LogFilterDialog, self).__init__(parent)
        self.accepted.connect(self.createFilter)

        self.operationCombo = QComboBox()
        self.operationCombo.addItems(LogFilterDialog.OPERATION_OPTIONS)
        self.tablenameCombo = QComboBox()
        self.tablenameCombo.addItems(LogFilterDialog.TABLENAME_OPTIONS)

        self.fromEdit = QDateTimeEdit()
        self.toEdit = QDateTimeEdit()

        groupLayout = QFormLayout()
        groupLayout.addRow("Od: ", self.fromEdit)
        groupLayout.addRow("Do: ", self.toEdit)
        groupLayout.addRow("Operace: ", self.operationCombo)
        groupLayout.addRow("Tabulka: ", self.tablenameCombo)

        rejectButton = QPushButton("Storno")
        rejectButton.clicked.connect(self.reject)
        acceptButton = QPushButton("OK")
        acceptButton.clicked.connect(self.accept)

        buttonsLayout = QHBoxLayout()
        buttonsLayout.addStretch(1)
        buttonsLayout.addWidget(acceptButton)
        buttonsLayout.addWidget(rejectButton)

        layout = QVBoxLayout()
        layout.addLayout(groupLayout)
        layout.addSpacing(12)
        layout.addLayout(buttonsLayout)
        self.setLayout(layout)

        self.setMinimumWidth(300)
        self.setWindowTitle("Filtrování logů")

    def initControls(self, filter_):
        selected = filter_.get('operation', '')
        try:
            index = LogFilterDialog.OPERATION_OPTIONS.index(selected)
        except ValueError:
            index = 0
        self.operationCombo.setCurrentIndex(index)

        selected = filter_.get('tablename', '')
        try:
            index = LogFilterDialog.TABLENAME_OPTIONS.index(selected)
        except ValueError:
            index = 0
        self.tablenameCombo.setCurrentIndex(index)

        start = filter_.get('start_datetime', None)
        if start is None:
            start = datetime.utcnow()
            start = calendar.timegm(start.timetuple()) - 3600*24
        else:
            start = calendar.timegm(start.timetuple())
        
        end = filter_.get('end_datetime', datetime.utcnow())
        end = calendar.timegm(end.timetuple())
        self.fromEdit.setDateTime(QDateTime.fromTime_t(start, TZ))
        self.toEdit.setDateTime(QDateTime.fromTime_t(end, TZ))

    def getFilter(self):
        filter_ = {}

        start = self.fromEdit.dateTime().toTime_t()
        end = self.toEdit.dateTime().toTime_t()
        filter_['start_datetime'] = datetime.utcfromtimestamp(start)
        filter_['end_datetime'] = datetime.utcfromtimestamp(end)
        if self.operationCombo.currentText():
            filter_['operation'] = self.operationCombo.currentText()
        if self.tablenameCombo.currentText():
            filter_['tablename'] = self.tablenameCombo.currentText()

        return filter_

    @pyqtSlot()
    def createFilter(self):
        self._filter = self.getFilter()

    def filter(self):
        return self._filter


def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)

