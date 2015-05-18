"""
Main application window.

Author: Tomas Krizek
"""

from ui_mainwindow import Ui_MainWindow
from PyQt5.QtWidgets import QMainWindow, QApplication, qApp

class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self):
        # Setup UI.
        super(MainWindow, self).__init__()
        self.setupUi(self)

        # Connect buttons to actions.
        # self.btnLoadGenerate.clicked.connect(self.actionGenerate.trigger)

        # Connect buttons or actions to function calls.
        # self.btnOutputFolder.clicked.connect(self.select_output_folder)
        # self.actionExit.triggered.connect(self.exit)
        # self.actionGenerate.triggered.connect(self.load_and_generate)

        # Initialize variables.
        
        # self.text_codec = QTextCodec.codecForName('UTF-16')

    def exit(self):
        qApp.quit()

    def _uconvert(self, text):
        """Converts QString encoding to Python unicode string."""
        return unicode(self.text_codec.fromUnicode(text), 'UTF-16')


def main():
    import sys
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()