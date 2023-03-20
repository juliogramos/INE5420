import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import Qt

from dataclasses import dataclass
from object import Point, Line, Wireframe
from novoPonto import UiPonto
from novaLinha import UiLinha
from novoPoligono import UiPoligono

@dataclass
class Container:
    xMin: int
    yMin: int
    xMax: int
    yMax: int

class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('testeui.ui', self)

        self.setCanvas()
        self.setPainter()
        self.setButtons()

        #Determina o nome do objeto
        self.indexes = [1, 1, 1]
        self.displayFile = []
        
        self.cgViewport = Container(400, 400, 800, 800)
        self.cgWindow = Container(0, 0, 1200, 1200)

        #self.draw_something()

    def viewportTransformationx(self, xw):
        xvp = (xw - self.cgWindow.xMin)/(self.cgWindow.xMax - self.cgWindow.xMin) * (self.cgViewport.xMax - self.cgViewport.xMin) 
        
        return round(xvp) 
    def viewportTransformationy(self, yw):
        yvp = (1 - ((yw - self.cgWindow.yMin)/(self.cgWindow.yMax - self.cgWindow.yMin))) * (self.cgViewport.yMax - self.cgViewport.yMin) 
        
        return round(yvp) 
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

    def novoPontoWindow(self):
        novoPontoDialog = UiPonto()
        if novoPontoDialog.exec_() and novoPontoDialog.xValue.text() and novoPontoDialog.yValue.text():
            print("Entrou ponto")
            x = self.viewportTransformationx(int(novoPontoDialog.xValue.text()))
            y = self.viewportTransformationy(int(novoPontoDialog.yValue.text()))
            print(x)
            print(y)
            novoPonto = Point(x, y, "Ponto {}".format(self.indexes[0]))
            self.displayFile.append(novoPonto)
            self.indexes[0] += 1
            self.objectList.addItem(novoPonto.name)
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
            print("Entrou linha")
            
            x1 = self.viewportTransformationx(int((novaLinhaDialog.xValue1.text()))) 
            x2 = self.viewportTransformationx(int((novaLinhaDialog.xValue2.text()))) 
            y1 = self.viewportTransformationy(int((novaLinhaDialog.yValue1.text()))) 
            y2 = self.viewportTransformationy(int((novaLinhaDialog.yValue2.text())))
            print(f"ponto 1 ({x1}, {y1})")
            print(f"ponto 2 ({x2}, {y2})")
            newLine = Line(Point(x1, y1, ""), Point(x2, y2, ""), "Linha {}".format(self.indexes[1]))
            self.displayFile.append(newLine)
            self.indexes[1] += 1
            self.objectList.addItem(newLine.name)
            newLine.draw(self.painter)

            self.status.addItem("Linha adicionada com sucesso.")
        else:

            self.status.addItem("Falha ao adicionar linha.")

        self.update()
    
    def novoPoligonoWindow(self):
        novoPoligonoDialog = UiPoligono()
        if novoPoligonoDialog.exec_() and novoPoligonoDialog.listaPontos:
            print("Entrou poligono")
            newPoly = Wireframe(novoPoligonoDialog.polyList, "Polígono {}".format(self.indexes[2]))
            self.displayFile.append(newPoly)
            self.indexes[2] += 1
            self.objectList.addItem(newPoly.name)
            newPoly.draw(self.painter)
            self.status.addItem("Polígono adicionado com sucesso.")
        else:
            self.status.addItem("Falha ao adicionar polígono.")
        self.update()

    #Fazer um método pra dar self.painter.end() no término do programa
