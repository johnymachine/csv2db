"""
RDB 2015

User Interface

Pagination Controls

Author: Tomas Krizek
"""

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QPushButton, QSpinBox)


class PaginationControls(QWidget):
    PAGE_ROW_COUNT = 10

    def __init__(self, parent=None):
        super(PaginationControls, self).__init__(parent)

        self.counter = QSpinBox(self)

        self.startButton = QPushButton(self)
        self.prevButton = QPushButton(self)
        self.nextButton = QPushButton(self)
        self.endButton = QPushButton(self)

        self.createGUI()

        self.updateControls()

    def createGUI(self):
        self.startButton.setText("<<")
        self.startButton.clicked.connect(self.on_startButton_clicked)

        self.prevButton.setText("<")
        self.prevButton.clicked.connect(self.on_prevButton_clicked)

        self.nextButton.setText(">")
        self.nextButton.clicked.connect(self.on_nextButton_clicked)

        self.endButton.setText(">>")
        self.endButton.clicked.connect(self.on_endButton_clicked)

        self.counter.valueChanged.connect(self.on_counter_valueChanged)

        layout = QHBoxLayout(self)
        layout.addWidget(self.startButton)
        layout.addWidget(self.prevButton)
        layout.addWidget(self.counter)
        layout.addWidget(self.nextButton)
        layout.addWidget(self.endButton)
        self.setLayout(layout)

    def updateControls(self):
        page = self.counter.value()

        self.startButton.setEnabled(True)
        self.prevButton.setEnabled(True)
        self.nextButton.setEnabled(True)
        self.endButton.setEnabled(True)

        # end conditions for button enables/disables
        if page == 0:
            self.startButton.setEnabled(False)
            self.prevButton.setEnabled(False)
        elif page == self.counter.maximum():
            self.endButton.setEnabled(False)
            self.nextButton.setEnabled(False)

    def setMaximum(self, maximum):
        self.counter.setMaximum(maximum)

    @pyqtSlot()
    def on_startButton_clicked(self):
        self.counter.setValue(0)

    @pyqtSlot()
    def on_prevButton_clicked(self):
        self.counter.setValue(self.counter.value() - 1)

    @pyqtSlot()
    def on_nextButton_clicked(self):
        self.counter.setValue(self.counter.value() + 1)

    @pyqtSlot()
    def on_endButton_clicked(self):
        self.counter.setValue(self.counter.maximum())

    @pyqtSlot(int)
    def on_counter_valueChanged(self, value):
        self.updateControls()


if __name__ == '__main__':

    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)

    widget = PaginationControls()
    widget.show()

    sys.exit(app.exec_())

