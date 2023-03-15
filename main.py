import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import Qt

from window import Ui

app = QtWidgets.QApplication(sys.argv)
window = Ui()
window.show()
app.exec_()