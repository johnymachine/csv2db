"""
RDB 2015

User Interface

Filter Widget for measurements

Author: Tomas Krizek
"""

from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import (QTableWidget, QTableWidgetItem, QWidget,
    QVBoxLayout, QPushButton, QAbstractItemView, QMessageBox, QLabel)

from PyQt5.QtCore import QDate, QSize, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QListView, QListWidget, QListWidgetItem, QPushButton, QSpinBox,
        QStackedWidget, QVBoxLayout, QWidget, QFormLayout, QDoubleSpinBox)


class BasicFilterPage(QWidget):
    def __init__(self, parent=None):
        super(BasicFilterPage, self).__init__(parent)

        self.blockCombo = QComboBox()
        self.deviceCombo = QComboBox()
        self.unitCombo = QComboBox()

        groupLayout = QFormLayout()
        groupLayout.addRow("Skupina měření:", self.blockCombo)
        groupLayout.addRow("Přístroj:", self.deviceCombo)
        groupLayout.addRow("Veličina:", self.unitCombo)

        filterGroup = QGroupBox("Základní filtry")
        filterGroup.setLayout(groupLayout)

        self.valuesOffCheckbox = QCheckBox()
        valuesLayout = QFormLayout()
        valuesLayout.addRow("Mimo odchylku:", self.valuesOffCheckbox)

        valuesGroup = QGroupBox("Hodnoty")
        valuesGroup.setLayout(valuesLayout)

        layout = QVBoxLayout()
        layout.addWidget(filterGroup)
        layout.addSpacing(12)
        layout.addWidget(valuesGroup)
        layout.addStretch(1)

        self.setLayout(layout)

    def setBlockOptions(self, blockOptions):
        self.blockCombo.clear()
        blockOptions.insert(0, '')
        self.blockCombo.addItems([str(option) for option in blockOptions])

    def setDeviceOptions(self, deviceOptions):
        self.deviceCombo.clear()
        deviceOptions.insert(0, '')
        self.deviceCombo.addItems([str(option) for option in deviceOptions])

    def setUnitOptions(self, unitOptions):
        self.unitCombo.clear()
        unitOptions.insert(0, '')
        self.unitCombo.addItems([str(option) for option in unitOptions])



class DateTimeFilterPage(QWidget):
    def __init__(self, parent=None):
        super(DateTimeFilterPage, self).__init__(parent)

        self.fromEdit = QDateTimeEdit()
        self.toEdit = QDateTimeEdit()

        groupLayout = QFormLayout()
        groupLayout.addRow("Od:", self.fromEdit)
        groupLayout.addRow("Do:", self.toEdit)

        group = QGroupBox("Datum a čas")
        group.setCheckable(True)
        group.setChecked(False)
        group.setLayout(groupLayout)

        layout = QVBoxLayout()
        layout.addWidget(group)
        layout.addStretch(1)

        self.setLayout(layout)


class LocationFilterPage(QWidget):
    def __init__(self, parent=None):
        super(LocationFilterPage, self).__init__(parent)

        self.xSpinBox = QDoubleSpinBox()
        self.xSpinBox.setMinimum(float('-inf'))
        self.xSpinBox.setMaximum(float('inf'))
        
        self.ySpinBox = QDoubleSpinBox()
        self.ySpinBox.setMinimum(float('-inf'))
        self.ySpinBox.setMaximum(float('inf'))

        self.tolSpinBox = QDoubleSpinBox()
        self.tolSpinBox.setMinimum(float('-inf'))
        self.tolSpinBox.setMaximum(float('inf'))

        groupLayout = QFormLayout()
        groupLayout.addRow("X:", self.xSpinBox)
        groupLayout.addRow("Y:", self.ySpinBox)
        groupLayout.addRow("Tolerance:", self.tolSpinBox)

        group = QGroupBox("Lokace")
        group.setCheckable(True)
        group.setChecked(False)
        group.setLayout(groupLayout)

        layout = QVBoxLayout()
        layout.addWidget(group)
        layout.addStretch(1)

        self.setLayout(layout)


class ConfigDialog(QDialog):
    def __init__(self, parent=None):
        super(ConfigDialog, self).__init__(parent)

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

        closeButton = QPushButton("Close")

        self.createIcons()
        self.contentsWidget.setCurrentRow(0)

        closeButton.clicked.connect(self.close)

        horizontalLayout = QHBoxLayout()
        horizontalLayout.addWidget(self.contentsWidget)
        horizontalLayout.addWidget(self.pagesWidget, 1)

        buttonsLayout = QHBoxLayout()
        buttonsLayout.addStretch(1)
        buttonsLayout.addWidget(closeButton)

        layout = QVBoxLayout()
        layout.addLayout(horizontalLayout)
        layout.addStretch(1)
        layout.addSpacing(12)
        layout.addLayout(buttonsLayout)

        self.setLayout(layout)

        self.setWindowTitle("Filtrování výsledků")

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


if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    dialog = ConfigDialog()
    dialog.basicFilterPage.setBlockOptions([2,3, 4, 5])
    dialog.basicFilterPage.setDeviceOptions(['dsa2', 'rm -rf'])
    dialog.basicFilterPage.setUnitOptions(['A', 'm^2'])
    sys.exit(dialog.exec_())    
