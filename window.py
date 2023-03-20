import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import Qt

from object import Point, Line, Wireframe
from novoPonto import UiPonto
from novaLinha import UiLinha
from novoPoligono import UiPoligono

class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('testeui.ui', self)

        self.setCanvas()
        self.setPainter()
        self.setButtons()

        #self.draw_something()


    def setCanvas(self):
        self.canvas = QtGui.QPixmap(400, 400)
        self.canvas.fill(Qt.white)
        self.mainLabel.setPixmap(self.canvas)

    def setPainter(self):
        self.painter = QtGui.QPainter(self.mainLabel.pixmap())
        self.pen = QtGui.QPen(Qt.red)
        self.pen.setWidth(5)
        self.painter.setPen(self.pen)

    def setButtons(self):
        self.newPoint.clicked.connect(self.novoPontoWindow)
        self.newLine.clicked.connect(self.novaLinhaWindow)
        self.newPoligon.clicked.connect(self.novoPoligonoWindow)
    def draw_something(self):
        p1 = Point(50, 200)
        p2 = Point (300, 300)
        l1 = Line(Point(5,5), Point(105, 105))
        l2 = Line(Point(200,400), Point(200, 0))
        objList = [p1, p2, l1, l2]

        for obj in objList:
            obj.draw(self.painter)
    def novoPoligonoWindow(self):
        novoPoligonoDialog = UiPoligono()
        pontos = []
        
        #novoPoligonoDialog.newPoint.clicked.connect(self.update())
        novoPoligonoDialog.buildPoligon.clicked.connect(lambda: Wireframe(pontos).draw(self.painter))
        while (True):
            if novoPoligonoDialog.exec_(): 
                if novoPoligonoDialog.xValue.text() and novoPoligonoDialog.yValue.text():
                    print("oi")
                    x = int(novoPoligonoDialog.xValue.text())
                    y = int(novoPoligonoDialog.yValue.text())
                    pontos.append(Point(x, y))
                    print(pontos)
                    novoPoligonoDialog.xValue.clear()
                    novoPoligonoDialog.yValue.clear()
        self.update()
    def novoPontoWindow(self):
        novoPontoDialog = UiPonto()
        if novoPontoDialog.exec_() and novoPontoDialog.xValue.text() and novoPontoDialog.yValue.text():
            print("entrou")
            x = int(novoPontoDialog.xValue.text())
            y = int(novoPontoDialog.yValue.text())
            print(x)
            print(y)
            novoPonto = Point(x, y)
            novoPonto.draw(self.painter)

            self.status.addItem("Ponto adicionado com sucesso.")
        else:
            self.status.addItem("Falha ao adicionar ponto.")

        #ADICIONAR PONTO NA LISTA
        #COLOCAR LISTA EM UM LUGAR MELHOR
        #FAZER UMA FUNÇÃO QUE UPDATA TUDO NA LISTA

        self.update()

    def novaLinhaWindow(self):
        novaLinhaDialog = UiLinha()
        if novaLinhaDialog.exec_() and novaLinhaDialog.xValue1.text() and novaLinhaDialog.xValue2.text() and novaLinhaDialog.yValue1.text() and novaLinhaDialog.yValue2.text():
            print("entrou")
            
            x1 = int(novaLinhaDialog.xValue1.text()) 
            x2 = int(novaLinhaDialog.xValue2.text()) 
            y1 = int(novaLinhaDialog.yValue1.text()) 
            y2 = int(novaLinhaDialog.yValue2.text()) 
            print(f"ponto 1 ({x1}, {y1})")
            print(f"ponto 2 ({x2}, {y2})")
            newLine = Line(Point(x1, y1), Point(x2, y2))
            newLine.draw(self.painter)

            self.status.addItem("Linha adicionada com sucesso.")
        else:

            self.status.addItem("Falha ao adicionar linha.")

        self.update()
    #Fazer um método pra dar self.painter.end() no término do programa
