"""
RDB 2015

User Interface

Export Dialog

Author: Tomas Krizek
"""

from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import (QApplication, QDialog, QGridLayout, QLabel,
    QHBoxLayout, QMessageBox, QPushButton, QVBoxLayout, QWidget, QFileDialog)

from .. import database as db
from .filteringwidget import FilteringWidget


class ExportDialog(QDialog):
    def __init__(self, parent=None):
        super(ExportDialog, self).__init__(parent)

        self.filter = {}
        self.filename = ''

        self.msgBox = QMessageBox(self)
        self.msgBox.setIcon(QMessageBox.Information)

        self.filteringWidget = FilteringWidget()
        self.filteringWidget.filterChanged.connect(self.on_filterChanged)
        self.filteringWidget.setContentsMargins(0, 0, 0, 0)

        self.fileChooserWidget = FileChooserWidget()
        self.fileChooserWidget.filenameChanged.connect(
            self.on_filenameChanged)

        groupLayout = QGridLayout()
        groupLayout.addWidget(self.filteringWidget, 0, 0, 1, 2)
        groupLayout.addWidget(QLabel('Výstupní soubor: '), 1, 0)
        groupLayout.addWidget(self.fileChooserWidget, 1, 1)
        groupLayout.setColumnStretch(1, 1)
        groupLayout.setContentsMargins(0, 0, 0, 0)
        groupLayout.setHorizontalSpacing(0)

        self.exportButton = QPushButton("Export")
        self.exportButton.clicked.connect(self.on_exportClicked)
        
        self.cancelButton = QPushButton("Storno")
        self.cancelButton.clicked.connect(self.reject)

        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(self.exportButton)
        buttonLayout.addWidget(self.cancelButton)

        layout = QVBoxLayout()
        layout.addLayout(groupLayout)
        layout.addSpacing(30)
        layout.addLayout(buttonLayout)
        self.setLayout(layout)

        self.setWindowTitle("Export")
        self.setMinimumWidth(500)
        self.setModal(True)

    def setFilename(self, filename):
        self.filename = filename

    def setFilterOptions(self, options):
        self.filteringWidget.setOptions(options)

    def setFilter(self, filter_):
        self.filteringWidget.setFilter(filter_)

    @pyqtSlot(dict)
    def on_filterChanged(self, filter_):
        self.filter = filter_

    @pyqtSlot(str)
    def on_filenameChanged(self, filename):
        self.filename = filename

    @pyqtSlot()
    def on_exportClicked(self):
        if not self.filename:
            QMessageBox.critical(self, 'Není vybrán soubor',
                'Vyberte soubor pro export dat!')
            return
        self.setEnabled(False)

        db.execute(db.export_data, self.on_exportFinished,
            self.filename, filter_=self.filter)

        self.msgBox.setEnabled(True)
        self.msgBox.setWindowTitle('Probíhá export')
        self.msgBox.setText('Prosím čekejte...')
        self.msgBox.setStandardButtons(QMessageBox.NoButton)
        self.msgBox.exec_()

    def on_exportFinished(self, *args):
        self.setEnabled(True)
        self.msgBox.setWindowTitle('Dokončeno')
        self.msgBox.setText('Export proběhl úspěšně.')
        self.msgBox.setStandardButtons(QMessageBox.Ok)
        self.msgBox.finished.connect(self.accept)

    def closeEvent(self, event):
        if not self.isEnabled():
            event.ignore()
        else:
            event.accept()


class FileChooserWidget(QWidget):

    filenameChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        super(FileChooserWidget, self).__init__(parent)

        self.label = QLabel()
        self.button = QPushButton('Vybrat soubor...')
        self.button.clicked.connect(self.on_button_clicked)

        layout = QHBoxLayout()
        layout.addWidget(self.label)
        layout.setStretch(0, 1)
        layout.addWidget(self.button)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    @pyqtSlot()
    def on_button_clicked(self):
        caption = 'Vyberte výstupní soubor'
        dialog = QFileDialog(self, caption)
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setAcceptMode(QFileDialog.AcceptSave)
        dialog.setNameFilter('CSV soubory (*.csv)')
        dialog.setDefaultSuffix('csv')
        if dialog.exec_():
            self.setFilename(dialog.selectedFiles()[0])

    def setFilename(self, filename):
        self.filename = filename
        self.label.setText(self.filename)
        self.filenameChanged.emit(self.filename)

    def filename(self):
        return self.filename
