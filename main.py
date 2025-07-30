import sys
import ui
from PySide6.QtWidgets import QApplication

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = ui.MainWindow()
    win.show()
    app.exec()
