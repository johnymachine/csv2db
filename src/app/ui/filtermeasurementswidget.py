"""
RDB 2015

User Interface

Filter Widget for measurements

Author: Tomas Krizek
"""

from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QTimeZone, QDateTime
from PyQt5.QtWidgets import (QTableWidget, QTableWidgetItem, QWidget,
    QVBoxLayout, QPushButton, QAbstractItemView, QMessageBox, QLabel)

from PyQt5.QtCore import QDate, QSize, Qt, QTimeZone
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QListView, QListWidget, QListWidgetItem, QPushButton, QSpinBox,
        QStackedWidget, QVBoxLayout, QWidget, QFormLayout, QDoubleSpinBox)

from datetime import datetime
import calendar

TZ = QTimeZone('Europe/Prague')

class BasicFilterPage(QWidget):
    def __init__(self, parent=None):
        super(BasicFilterPage, self).__init__(parent)

        self.blockCombo = QComboBox()
        self.deviceCombo = QComboBox()
        self.unitCombo = QComboBox()

        self.combos = {'block': self.blockCombo, \
                       'device': self.deviceCombo, \
                       'unit': self.unitCombo}

        groupLayout = QFormLayout()
        groupLayout.addRow("Skupina měření:", self.blockCombo)
        groupLayout.addRow("Přístroj:", self.deviceCombo)
        groupLayout.addRow("Veličina:", self.unitCombo)

        filterGroup = QGroupBox("Základní filtry")
        filterGroup.setLayout(groupLayout)

        self.deviatedValuesCheckbox = QCheckBox()
        valuesLayout = QFormLayout()
        valuesLayout.addRow("Mimo odchylku:", self.deviatedValuesCheckbox)

        valuesGroup = QGroupBox("Hodnoty")
        valuesGroup.setLayout(valuesLayout)

        layout = QVBoxLayout()
        layout.addWidget(filterGroup)
        layout.addSpacing(12)
        layout.addWidget(valuesGroup)
        layout.addStretch(1)

        self.setLayout(layout)

    def setComboOptions(self, combo, options, selected=''):
        options.insert(0, '')
        options = [str(option) for option in options]

        index = options.index(str(selected))
        if index == -1:
            index = 0

        combo.clear()
        combo.addItems(options)
        combo.setCurrentIndex(index)

    def getFilter(self):
        filter_ = {}

        for name, combo in self.combos.items():
            selected = combo.currentText()
            if selected:
                filter_[name] = selected

        filter_['deviated_values'] = bool(self.deviatedValuesCheckbox.checkState())

        return filter_

    def initControls(self, options, filter_):
        for name, combo in self.combos.items():
            try:
                comboOptions = options[name]
            except KeyError:
                continue
            else:
                selectedOption = filter_.get(name, '')
                self.setComboOptions(combo, comboOptions, selectedOption)

        checked = filter_.get('deviated_values', False)
        self.deviatedValuesCheckbox.setChecked(checked)


class DateTimeFilterPage(QWidget):
    def __init__(self, parent=None):
        super(DateTimeFilterPage, self).__init__(parent)

        self.fromEdit = QDateTimeEdit()
        self.toEdit = QDateTimeEdit()

        groupLayout = QFormLayout()
        groupLayout.addRow("Od:", self.fromEdit)
        groupLayout.addRow("Do:", self.toEdit)

        self.group = QGroupBox("Datum a čas")
        self.group.setCheckable(True)
        self.group.setChecked(False)
        self.group.setLayout(groupLayout)

        layout = QVBoxLayout()
        layout.addWidget(self.group)
        layout.addStretch(1)

        self.setLayout(layout)

    def initControls(self, filter_):
        self.group.setChecked(False)

        for key in ['start_datetime', 'end_datetime']:
            if key in filter_:
                self.group.setChecked(True)
                break

        start = filter_.get('start_datetime', datetime.utcnow())
        start = calendar.timegm(start.timetuple())
        end = filter_.get('end_datetime', datetime.utcnow())
        end = calendar.timegm(end.timetuple())
        self.fromEdit.setDateTime(QDateTime.fromTime_t(start, TZ))
        self.toEdit.setDateTime(QDateTime.fromTime_t(end, TZ))

    def getFilter(self):
        filter_ = {}

        if self.group.isChecked():
            start = self.fromEdit.dateTime().toTime_t()
            end = self.toEdit.dateTime().toTime_t()
            filter_['start_datetime'] = datetime.utcfromtimestamp(start)
            filter_['end_datetime'] = datetime.utcfromtimestamp(end)

        return filter_


class LocationFilterPage(QWidget):
    def __init__(self, parent=None):
        super(LocationFilterPage, self).__init__(parent)

        self.xSpinBox = QDoubleSpinBox()
        self.xSpinBox.setMinimum(float('-inf'))
        self.xSpinBox.setMaximum(float('inf'))
        self.xSpinBox.setDecimals(6)

        self.ySpinBox = QDoubleSpinBox()
        self.ySpinBox.setMinimum(float('-inf'))
        self.ySpinBox.setMaximum(float('inf'))
        self.ySpinBox.setDecimals(6)

        self.tolSpinBox = QDoubleSpinBox()
        self.tolSpinBox.setMinimum(float('-inf'))
        self.tolSpinBox.setMaximum(float('inf'))
        self.tolSpinBox.setDecimals(6)

        groupLayout = QFormLayout()
        groupLayout.addRow("X:", self.xSpinBox)
        groupLayout.addRow("Y:", self.ySpinBox)
        groupLayout.addRow("Tolerance:", self.tolSpinBox)

        self.group = QGroupBox("Lokace")
        self.group.setCheckable(True)
        self.group.setChecked(False)
        self.group.setLayout(groupLayout)

        layout = QVBoxLayout()
        layout.addWidget(self.group)
        layout.addStretch(1)

        self.setLayout(layout)

    def initControls(self, filter_):
        self.group.setChecked(False)

        for key in ['loc_x', 'loc_y', 'loc_tol']:
            if key in filter_:
                self.group.setChecked(True)
                break

        self.xSpinBox.setValue(filter_.get('loc_x', 0))
        self.ySpinBox.setValue(filter_.get('loc_y', 0))
        self.tolSpinBox.setValue(filter_.get('loc_tol', 0))

    def getFilter(self):
        filter_ = {}

        if self.group.isChecked():
            filter_['loc_x'] = self.xSpinBox.value()
            filter_['loc_y'] = self.ySpinBox.value()
            filter_['loc_tol'] = self.tolSpinBox.value()

        return filter_


class ConfigDialog(QDialog):

    def __init__(self, parent=None):
        super(ConfigDialog, self).__init__(parent)

        self.accepted.connect(self.createFilter)

        self.contentsWidget = QListWidget()
        self.contentsWidget.setViewMode(QListView.IconMode)
        self.contentsWidget.setIconSize(QSize(96, 84))
        self.contentsWidget.setMovement(QListView.Static)
        self.contentsWidget.setMaximumWidth(128)
        self.contentsWidget.setSpacing(12)

        self.basicFilterPage = BasicFilterPage()
        self.timeFilterPage = DateTimeFilterPage()
        self.locationFilterPage = LocationFilterPage()

        self.pagesWidget = QStackedWidget()
        self.pagesWidget.addWidget(self.basicFilterPage)
        self.pagesWidget.addWidget(self.timeFilterPage)
        self.pagesWidget.addWidget(self.locationFilterPage)
        self.pagesWidget.setMinimumHeight(360)

        rejectButton = QPushButton("Storno")
        rejectButton.clicked.connect(self.reject)
        acceptButton = QPushButton("OK")
        acceptButton.clicked.connect(self.accept)

        self.createIcons()
        self.contentsWidget.setCurrentRow(0)

        horizontalLayout = QHBoxLayout()
        horizontalLayout.addWidget(self.contentsWidget)
        horizontalLayout.addWidget(self.pagesWidget, 1)

        buttonsLayout = QHBoxLayout()
        buttonsLayout.addStretch(1)
        buttonsLayout.addWidget(acceptButton)
        buttonsLayout.addWidget(rejectButton)

        layout = QVBoxLayout()
        layout.addLayout(horizontalLayout)
        layout.addStretch(1)
        layout.addSpacing(12)
        layout.addLayout(buttonsLayout)

        self.setLayout(layout)

        self.setWindowTitle("Filtrování výsledků")

    def initControls(self, options, filter_):
        self.basicFilterPage.initControls(options, filter_)
        self.timeFilterPage.initControls(filter_)
        self.locationFilterPage.initControls(filter_)

    def changePage(self, current, previous):
        if not current:
            current = previous

        self.pagesWidget.setCurrentIndex(self.contentsWidget.row(current))

    def createIcons(self):
        basicButton = QListWidgetItem(self.contentsWidget)
        basicButton.setIcon(QIcon('app/ui/images/settings.png'))
        basicButton.setText("Základní filtry")
        basicButton.setTextAlignment(Qt.AlignHCenter)
        basicButton.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

        timeButton = QListWidgetItem(self.contentsWidget)
        timeButton.setIcon(QIcon('app/ui/images/time.png'))
        timeButton.setText("Datum a čas")
        timeButton.setTextAlignment(Qt.AlignHCenter)
        timeButton.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

        locationButton = QListWidgetItem(self.contentsWidget)
        locationButton.setIcon(QIcon('app/ui/images/location.png'))
        locationButton.setText("Lokace")
        locationButton.setTextAlignment(Qt.AlignHCenter)
        locationButton.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

        self.contentsWidget.currentItemChanged.connect(self.changePage)

    @pyqtSlot()
    def createFilter(self):
        self.filter = self.basicFilterPage.getFilter()
        self.filter.update(self.timeFilterPage.getFilter())
        self.filter.update(self.locationFilterPage.getFilter())
        print(self.filter)        


if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    dialog = ConfigDialog()
    
    options = {'block': [1, 2, 3, 4, 5], \
               'device': ['rm2-x', 'zc-3d', 'qap'], \
               'unit': ['Hz', 'A', 'm^2']}
    filter_ = {'block': 4, 'unit': 'Hz', 'deviated_values': True, \
               'start_datetime': datetime(2015,5,7,10), 'loc_x': -32.4255}

    dialog.initControls(options, filter_)

    sys.exit(dialog.exec_())
