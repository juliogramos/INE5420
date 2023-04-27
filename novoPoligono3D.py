import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import Qt

from novoPonto3D import UiPonto3D
from novaAresta import UiAresta
from object import Point3D

class UiPoligono3D(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi('novopoligono3d.ui', self)

        self.polyList = []
        self.edgeList = []
        
        self.pontoIndex = 0
        self.arestaIndex = 0

        self.novoPonto.clicked.connect(self.novoPontoWindow)
        self.novaAresta.clicked.connect(self.novaArestaWindow)

    def novoPontoWindow(self):
        novoPontoDialog = UiPonto3D()
        if novoPontoDialog.exec_() and novoPontoDialog.xValue.text() and novoPontoDialog.yValue.text():
            print("Entrou ponto")
            x = int(novoPontoDialog.xValue.text())
            y = int(novoPontoDialog.yValue.text())
            z = int(novoPontoDialog.zValue.text())
            print(x)
            print(y)
            novoPonto = Point3D(x, y, z)
            self.polyList.append(novoPonto)
            self.listaPontos.addItem("{}: Ponto ({},{},{})".format(self.pontoIndex,x,y,z))
            self.pontoIndex += 1
        self.update()
        
    def novaArestaWindow(self):
        novaArestaDialog = UiAresta()
        if novaArestaDialog.exec_() and novaArestaDialog.p1.text() and novaArestaDialog.p2.text():
            if (int(novaArestaDialog.p1.text()) < 0) or (
                int(novaArestaDialog.p1.text()) >= len(self.polyList)): return
            if (int(novaArestaDialog.p2.text()) < 0) or (
                int(novaArestaDialog.p2.text()) >= len(self.polyList)): return
            
            p1 = int(novaArestaDialog.p1.text())
            p2 = int(novaArestaDialog.p2.text())
            self.edgeList.append((p1, p2))
            self.listaArestas.addItem("{}: Aresta ({} -> {})".format(self.arestaIndex, p1, p2))
            self.arestaIndex += 1
        self.update()


    #Fazer um método pra dar self.painter.end() no término do programa
