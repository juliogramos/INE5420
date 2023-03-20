import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import Qt

class UiPoligono(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi('novopoligono.ui', self)

    #Fazer um método pra dar self.painter.end() no término do programa
