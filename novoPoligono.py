import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import Qt

from novoPonto import UiPonto
from object import Point

class UiPoligono(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi('novopoligono.ui', self)

        self.polyList = []

        self.novoPonto.clicked.connect(self.novoPontoWindow)

    def novoPontoWindow(self):
        novoPontoDialog = UiPonto()
        if novoPontoDialog.exec_() and novoPontoDialog.xValue.text() and novoPontoDialog.yValue.text():
            print("Entrou ponto")
            x = int(novoPontoDialog.xValue.text())
            y = int(novoPontoDialog.yValue.text())
            print(x)
            print(y)
            novoPonto = Point(x, y, "")
            self.polyList.append(novoPonto)
            self.listaPontos.addItem("Novo ponto em {},{}".format(x,y))
        self.update()


    #Fazer um método pra dar self.painter.end() no término do programa
