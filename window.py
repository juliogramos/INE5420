import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import Qt

from dataclasses import dataclass
from object import Point, Line, Wireframe
from novoPonto import UiPonto
from novaLinha import UiLinha
from novoPoligono import UiPoligono

def clamp(n, inferior, superior):
    return max(inferior, min(n, superior))

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

        self.vpSize = [400, 400, 800, 800]
        self.wSize = [0, 0, 1200, 1200]
        
        self.cgViewport = Container(self.vpSize[0], self.vpSize[1], self.vpSize[2], self.vpSize[3])
        self.cgWindow = Container(self.wSize[0], self.wSize[1], self.wSize[2], self.wSize[3])

        #self.draw_something()
    

    def viewportTransformation(self, point):
        xvp = (point.x - self.cgWindow.xMin)/(self.cgWindow.xMax - self.cgWindow.xMin) * (self.cgViewport.xMax - self.cgViewport.xMin) 
        yvp = (1 - ((point.y - self.cgWindow.yMin)/(self.cgWindow.yMax - self.cgWindow.yMin))) * (self.cgViewport.yMax - self.cgViewport.yMin)

        return (round(xvp), round(yvp))
    
    def setCanvas(self):
        canvas = QtGui.QPixmap(400, 400)
        canvas.fill(Qt.white)
        self.mainLabel.setPixmap(canvas)

    def setPainter(self):
        self.painter = QtGui.QPainter(self.mainLabel.pixmap())
        self.pen = QtGui.QPen(Qt.red)
        self.pen.setWidth(5)
        self.painter.setPen(self.pen)

    def setButtons(self):
        self.newPoint.clicked.connect(self.novoPontoWindow)
        self.newLine.clicked.connect(self.novaLinhaWindow)
        self.newPoligon.clicked.connect(self.novoPoligonoWindow)

        self.zoomPlus.clicked.connect(self.zoomViewportIn)
        self.zoomMinus.clicked.connect(self.zoomViewportOut)

        self.panRightButton.clicked.connect(self.panRight)
        self.panLeftButton.clicked.connect(self.panLeft)
        self.panUpButton.clicked.connect(self.panUp)
        self.panDownButton.clicked.connect(self.panDown)

        self.RestoreButtom.clicked.connect(self.restoreOriginal)
        self.limpa.clicked.connect(self.drawAll)

    def drawOne(self, object):
        if object.type == "Point":
            (x, y) = self.viewportTransformation(object)
            print(x)
            print(y)
            self.painter.drawPoint(x, y)
        elif object.type == "Line":
            (x1, y1) = self.viewportTransformation(object.p1)
            (x2,y2) = self.viewportTransformation(object.p2)
            print(f"ponto 1 ({x1}, {y1})")
            print(f"ponto 2 ({x2}, {y2})")
            self.painter.drawLine(x1, y1, x2, y2)
        elif object.type == "Polygon":
            ps = []
            for p in object.points:
                ps.append(self.viewportTransformation(p))
            
            for i in range(1, len(ps)):
                self.painter.drawLine(ps[i-1][0], ps[i-1][1], ps[i][0], ps[i][1])
            self.painter.drawLine(ps[-1][0], ps[-1][1], ps[0][0], ps[0][1])

    def drawAll(self):
        self.mainLabel.pixmap().fill(Qt.white)
        for object in self.displayFile:
            self.drawOne(object)
        self.update()

    def novoPontoWindow(self):
        novoPontoDialog = UiPonto()
        if novoPontoDialog.exec_() and novoPontoDialog.xValue.text() and novoPontoDialog.yValue.text():
            print("Entrou ponto")
            x = int(novoPontoDialog.xValue.text())
            y = int(novoPontoDialog.yValue.text())
            novoPonto = Point(x, y, "Ponto {}".format(self.indexes[0]))
            self.displayFile.append(novoPonto)
            self.indexes[0] += 1
            self.objectList.addItem(novoPonto.name)
            #novoPonto.draw(self.painter)
            self.drawOne(novoPonto)

            self.status.addItem("Ponto adicionado com sucesso.")
        else:
            self.status.addItem("Falha ao adicionar ponto.")

        self.update()

    def novaLinhaWindow(self):
        novaLinhaDialog = UiLinha()
        if novaLinhaDialog.exec_() and novaLinhaDialog.xValue1.text() and novaLinhaDialog.xValue2.text() and novaLinhaDialog.yValue1.text() and novaLinhaDialog.yValue2.text():
            print("Entrou linha")
            
            x1 = int(novaLinhaDialog.xValue1.text())
            x2 = int(novaLinhaDialog.xValue2.text())
            y1 = int(novaLinhaDialog.yValue1.text())
            y2 = int(novaLinhaDialog.yValue2.text())
            newLine = Line(Point(x1, y1, ""), Point(x2, y2, ""), "Linha {}".format(self.indexes[1]))
            self.displayFile.append(newLine)
            self.indexes[1] += 1
            self.objectList.addItem(newLine.name)
            self.drawOne(newLine)

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
            self.drawOne(newPoly)
            self.status.addItem("Polígono adicionado com sucesso.")
        else:
            self.status.addItem("Falha ao adicionar polígono.")
        self.update()

    def zoomViewportIn(self):
        #clamp()
        self.cgViewport.xMax += 10
        self.cgViewport.xMin -= 10
        self.cgViewport.yMax += 10
        self.cgViewport.yMin -= 10
        self.drawAll()

    def zoomViewportOut(self):
        #clamp()
        self.cgViewport.xMax -= 10
        self.cgViewport.xMin += 10
        self.cgViewport.yMax -= 10
        self.cgViewport.yMin += 10
        self.drawAll()

    def panRight(self):
        #clamp()
        self.cgWindow.xMax += 100
        self.cgWindow.xMin += 100
        self.drawAll()

    def panLeft(self):
        #clamp()
        self.cgWindow.xMax -= 100
        self.cgWindow.xMin -= 100
        self.drawAll()
    
    def panUp(self):
        #clamp()
        self.cgWindow.yMax += 100
        self.cgWindow.yMin += 100
        self.drawAll()

    def panDown(self):
        #clamp()
        self.cgWindow.yMax -= 100
        self.cgWindow.yMin -= 100
        self.drawAll()

    def restoreOriginal(self):
        self.cgViewport.xMin = self.vpSize[0]
        self.cgViewport.yMin = self.vpSize[1]
        self.cgViewport.xMax = self.vpSize[2]
        self.cgViewport.yMax = self.vpSize[3]
    
        self.cgWindow.xMin = self.wSize[0]
        self.cgWindow.yMin = self.wSize[1]
        self.cgWindow.xMax = self.wSize[2]
        self.cgWindow.yMax = self.wSize[3]
        
        self.drawAll()
    #Fazer um método pra dar self.painter.end() no término do programa
