import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import Qt
import numpy as np

from dataclasses import dataclass
from object import Point, Line, Wireframe
from novoPonto import UiPonto
from novaLinha import UiLinha
from novoPoligono import UiPoligono
from transformacao import UiTransforma

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

        self.vpSize = [0, 0, 400, 400]
        self.wSize = [0, 0, 400, 400]
        
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

        self.transButton.clicked.connect(self.transformaWindow)

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

    #FUNCOES DE JANELA

    def novoPontoWindow(self):
        novoPontoDialog = UiPonto()
        if novoPontoDialog.exec_() and novoPontoDialog.xValue.text() and novoPontoDialog.yValue.text():
            print("Entrou ponto")
            print(self.pen.color())
            x = int(novoPontoDialog.xValue.text())
            y = int(novoPontoDialog.yValue.text())
            novoPonto = Point(x, y, "Ponto {}".format(self.indexes[0]))
            self.displayFile.append(novoPonto)
            self.indexes[0] += 1
            self.objectList.addItem(novoPonto.name)
            #novoPonto.draw(self.painter)
            if novoPontoDialog.rValue.text() and novoPontoDialog.gValue.text() and novoPontoDialog.bValue.text():
            
                self.pen = QtGui.QPen((QtGui.QColor(int(novoPontoDialog.rValue.text()), int(novoPontoDialog.gValue.text()), int(novoPontoDialog.bValue.text()), 255))) 
                self.pen.setWidth(5)
                self.painter.setPen(self.pen)
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
            if novaLinhaDialog.rValue.text() and novaLinhaDialog.gValue.text() and novaLinhaDialog.bValue.text():
            
                self.pen = QtGui.QPen((QtGui.QColor(int(novaLinhaDialog.rValue.text()), int(novaLinhaDialog.gValue.text()), int(novaLinhaDialog.bValue.text()), 255))) 
                self.pen.setWidth(5)
                self.painter.setPen(self.pen)
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
            if novoPoligonoDialog.rValue.text() and novoPoligonoDialog.gValue.text() and novoPoligonoDialog.bValue.text():
            
                self.pen = QtGui.QPen((QtGui.QColor(int(novoPoligonoDialog.rValue.text()), int(novoPoligonoDialog.gValue.text()), int(novoPoligonoDialog.bValue.text()), 255))) 
                self.pen.setWidth(5)
                self.painter.setPen(self.pen)
            self.drawOne(newPoly)
            self.status.addItem("Polígono adicionado com sucesso.")
        else:
            self.status.addItem("Falha ao adicionar polígono.")
        self.update()

    def transformaWindow(self):
        if self.objectList.currentRow() == -1:
            self.status.addItem("Erro: nenhum objeto selecionado.")
            return

        transformaDialog = UiTransforma()
        if transformaDialog.exec_():
            if transformaDialog.transX.text() or transformaDialog.transY.text():
                obj = self.displayFile[self.objectList.currentRow()]
                print(obj.name)
                if transformaDialog.transX.text():
                    Dx = int(transformaDialog.transX.text())
                else:
                    Dx = 0

                if transformaDialog.transY.text():
                    Dy = int(transformaDialog.transY.text())
                else:
                    Dy = 0

                self.translacao(obj, Dx, Dy)
                self.status.addItem(obj.name + " transladado com sucesso.")
                self.drawAll()

            if transformaDialog.escX.text() or transformaDialog.escY.text():
                obj = self.displayFile[self.objectList.currentRow()]
                print(obj.name)

                if transformaDialog.escX.text():
                    Sx = int(transformaDialog.escX.text())
                else:
                    Sx = 1

                if transformaDialog.escY.text():
                    Sy = int(transformaDialog.escY.text())
                else:
                    Sy = 1

                self.escalonamento(obj, Sx, Sy)
                self.status.addItem(obj.name + " escalonado com sucesso.")
                self.drawAll()

            if transformaDialog.rot_angulo.text():
                obj = self.displayFile[self.objectList.currentRow()]
                print(obj.name)
                angulo = int(transformaDialog.rot_angulo.text())
                self.rotacao(obj, angulo, 
                             transformaDialog.rotOrigem.isChecked(), 
                             transformaDialog.rotObject.isChecked(),
                             transformaDialog.rotPoint.isChecked(),
                             transformaDialog.rotPointX.text(),
                             transformaDialog.rotPointY.text())
                self.status.addItem(obj.name + " rotacionado com sucesso.")
                self.drawAll()
                self.status.addItem(obj.name + " transformado com sucesso.")
    
    def find_center(self, obj):
        if obj.type == "Point":
            return (obj.x, obj.y)
        
        if obj.type == "Line":
            x = (obj.p1.x + obj.p2.x)/2
            y = (obj.p1.y + obj.p2.y)/2
            
            return (x, y)
        
        if obj.type == "Polygon":
            x, y = 0, 0
            for i in obj.points:
                x += i.x
                y += i.y 

            x, y = x//len(obj.points), y//len(obj.points)
            
            return (x, y)

    def translacao(self, obj, Dx, Dy):
        if obj.type == "Point":
            P = [obj.x, obj.y, 1]
            T = [   [1, 0, 0],
                    [0, 1, 0],
                    [Dx, Dy, 1]
                ]
            (X,Y,W) = np.matmul(P, T)
            obj.x = X
            obj.y = Y
        
        elif obj.type == "Line":
            P1 = [obj.p1.x, obj.p1.y, 1]
            P2 = [obj.p2.x, obj.p2.y, 1]
            T = [   [1, 0, 0],
                    [0, 1, 0],
                    [Dx, Dy, 1]
                ]
            (X1, Y1, W1) = np.matmul(P1, T)
            (X2, Y2, W2) = np.matmul(P2, T)
            obj.p1.x = X1
            obj.p1.y = Y1
            obj.p2.x = X2
            obj.p2.y = Y2

        elif obj.type == "Polygon":
            T = [   [1, 0, 0],
                    [0, 1, 0],
                    [Dx, Dy, 1]
                ]
            for p in obj.points:
                P = (p.x, p.y, 1)
                (X,Y,W) = np.matmul(P, T)
                p.x = X
                p.y = Y 

    def escalonamento(self, obj, Sx, Sy):
        centroInicial = self.find_center(obj)
        
        if obj.type == "Point":
            P = [obj.x, obj.y, 1]
            T = [   [Sx, 0, 0],
                    [0, Sy, 0],
                    [0, 0, 1]
                ]
            (X,Y,W) = np.matmul(P, T)
            obj.x = X
            obj.y = Y
        
        elif obj.type == "Line":
            P1 = [obj.p1.x, obj.p1.y, 1]
            P2 = [obj.p2.x, obj.p2.y, 1]
            T = [   [Sx, 0, 0],
                    [0, Sy, 0],
                    [0, 0, 1]
                ]
            (X1, Y1, W1) = np.matmul(P1, T)
            (X2, Y2, W2) = np.matmul(P2, T)
            obj.p1.x = X1
            obj.p1.y = Y1
            obj.p2.x = X2
            obj.p2.y = Y2

        elif obj.type == "Polygon":
            centroInicial = self.find_center(obj)

            T = [   [Sx, 0, 0],
                    [0, Sy, 0],
                    [0, 0, 1]
                ]
            for p in obj.points:
                P = (p.x, p.y, 1)
                (X,Y,W) = np.matmul(P, T)
                p.x = X
                p.y = Y 

        centroFinal = self.find_center(obj)
        dist = (centroInicial[0] - centroFinal[0], centroInicial[1] - centroFinal[1])
        #print(centroInicial)
        #print(centroFinal)
        #print(dist)
        self.translacao(obj, dist[0], dist[1])

    def rotacao(self, obj, degree, toOrigin, toObject, toPoint, pX, pY):
        centroInicial = self.find_center(obj)
        
        if toObject:
            self.translacao(obj, -centroInicial[0], -centroInicial[1])
        elif toPoint:
            #Nao sei se ta certo
            if not pX or not pY:
                self.status.addItem("Erro: ponto de rotação não especificado.")
                return
            self.translacao(obj, -int(pX), -int(pY))

        if obj.type == "Point":
            P = [obj.x, obj.y, 1]
            T = [   [np.cos(degree), -np.sin(degree), 0],
                    [np.sin(degree), np.cos(degree), 0],
                    [0, 0, 1]
                ]
            (X,Y,W) = np.matmul(P, T)
            obj.x = X
            obj.y = Y
        
        elif obj.type == "Line":
            P1 = [obj.p1.x, obj.p1.y, 1]
            P2 = [obj.p2.x, obj.p2.y, 1]
            T = [   [np.cos(degree), -np.sin(degree), 0],
                    [np.sin(degree), np.cos(degree), 0],
                    [0, 0, 1]
                ]
            (X1, Y1, W1) = np.matmul(P1, T)
            (X2, Y2, W2) = np.matmul(P2, T)
            obj.p1.x = X1
            obj.p1.y = Y1
            obj.p2.x = X2
            obj.p2.y = Y2

        elif obj.type == "Polygon":
            print(toOrigin)
            print(toObject)
            print(toPoint)
            T = [   [np.cos(degree), -np.sin(degree), 0],
                    [np.sin(degree), np.cos(degree), 0],
                    [0, 0, 1]
                 ]
            for p in obj.points:
                P = (p.x, p.y, 1)
                (X,Y,W) = np.matmul(P, T)
                p.x = X
                p.y = Y 

        if toObject:
            self.translacao(obj, centroInicial[0], centroInicial[1])
        elif toPoint:
            #Nao sei se ta certo
            self.translacao(obj, int(pX), int(pY))

    # FUNCOES DE VISUALIZACAO

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

    def printalista(self):
        print(self.objectList.currentRow())
    #Fazer um método pra dar self.painter.end() no término do programa
