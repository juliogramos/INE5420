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
from rotwindow import UiRotWin
from descritorobj import DescritorOBJ

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
        self.windowAngle = 0
        
        self.cgViewport = Container(self.vpSize[0], self.vpSize[1], self.vpSize[2], self.vpSize[3])
        self.cgWindow = Container(self.wSize[0], self.wSize[1], self.wSize[2], self.wSize[3])
        self.cgWindowPPC = Container(-1,-1,1,1)
        
        self.ppcMatrix =    [   [0, 0, 0],
                                [0, 0, 0],
                                [0, 0, 0]
                            ]
        
        self.descObj = DescritorOBJ()
        
        self.makePPCmatrix()
        self.applyPPCmatrixWindow()

        #self.draw_something()
    

    def viewportTransformation(self, point):
        #xvp = (point.cn_x - self.cgWindow.xMin)/(self.cgWindow.xMax - self.cgWindow.xMin) * (self.cgViewport.xMax - self.cgViewport.xMin) 
        #yvp = (1 - ((point.cn_y - self.cgWindow.yMin)/(self.cgWindow.yMax - self.cgWindow.yMin))) * (self.cgViewport.yMax - self.cgViewport.yMin)
        print(self.cgWindowPPC)
        xvp = (point.cn_x - self.cgWindowPPC.xMin)/(self.cgWindowPPC.xMax - self.cgWindowPPC.xMin) * (self.cgViewport.xMax - self.cgViewport.xMin) 
        yvp = (1 - ((point.cn_y - self.cgWindowPPC.yMin)/(self.cgWindowPPC.yMax - self.cgWindowPPC.yMin))) * (self.cgViewport.yMax - self.cgViewport.yMin)
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

        self.rotWindowButton.clicked.connect(self.rodaWindow)

        self.RestoreButtom.clicked.connect(self.restoreOriginal)

        self.loadButton.clicked.connect(self.loadObjs)

        self.limpa.clicked.connect(self.drawAll)

    def drawOne(self, object):
        self.applyPPCmatrixOne(object)

        self.pen = QtGui.QPen(QtGui.QColor(object.color[0], object.color[1], object.color[2], 255))
        self.pen.setWidth(5)
        self.painter.setPen(self.pen)
        
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
            novoPonto = Point(x, y, "Ponto {}".format(self.indexes[0]), 0, 0)
            self.displayFile.append(novoPonto)
            self.indexes[0] += 1
            self.objectList.addItem(novoPonto.name)
            #novoPonto.draw(self.painter)
            if novoPontoDialog.rValue.text() and novoPontoDialog.gValue.text() and novoPontoDialog.bValue.text():
                novoPonto.color = (QtGui.QColor(int(novoPontoDialog.rValue.text()), int(novoPontoDialog.gValue.text()), int(novoPontoDialog.bValue.text()), 255))
                #self.pen = QtGui.QPen((QtGui.QColor(int(novoPontoDialog.rValue.text()), int(novoPontoDialog.gValue.text()), int(novoPontoDialog.bValue.text()), 255))) 
                #self.pen.setWidth(5)
                #self.painter.setPen(self.pen)
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
                newLine.color = (QtGui.QColor(int(novaLinhaDialog.rValue.text()), int(novaLinhaDialog.gValue.text()), int(novaLinhaDialog.bValue.text()), 255))
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
                newPoly.color = (QtGui.QColor(int(novoPoligonoDialog.rValue.text()), int(novoPoligonoDialog.gValue.text()), int(novoPoligonoDialog.bValue.text()), 255))
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
                print("DEPOIS DE SAIR DA ROTAÇÃO: ")
                print("{}, {}\n{}, {}".format(obj.p1.x, obj.p1.y, obj.p2.x, obj.p2.y))
                print("------------------")
                self.status.addItem(obj.name + " rotacionado com sucesso.")
                self.drawAll()
                self.status.addItem(obj.name + " transformado com sucesso.")

    def rodaWindow(self):
        rotDialog = UiRotWin()
        if rotDialog.exec_():
            if rotDialog.rot_angulo.text():
                ang = int(rotDialog.rot_angulo.text())
                self.windowAngle -= ang
                self.makePPCmatrix()
                self.applyPPCmatrixWindow()
                self.drawAll()
    
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

    def find_window_center(self):
        x = (self.cgWindow.xMin + self.cgWindow.xMax)/2
        y = (self.cgWindow.yMin + self.cgWindow.yMax)/2
        return (x,y)

    def makePPCmatrix(self):
        width = self.cgWindow.xMax - self.cgWindow.xMin
        height = self.cgWindow.yMax - self.cgWindow.yMin
        center = self.find_window_center()
        matTrans =  [   [1, 0, 0],
                        [0, 1, 0],
                        [-center[0], -center[1], 1]
                    ]

        """ y = [0, 1]
        vup = [self.cgWindow.xMin, self.cgWindow.xMax]
        vupnorm = vup / np.linalg.norm(vup)
        ang  = np.arccos(np.clip(np.dot(y, vupnorm), -1.0, 1.0))
        print("ANG: ")
        print(ang) """

        ang = np.deg2rad(self.windowAngle)

        matRot =    [   [np.cos(ang), -np.sin(ang), 0],
                        [np.sin(ang), np.cos(ang), 0],
                        [0, 0, 1]
                    ]
        
        matScale =  [   [2/width,   0,          0],
                        [0,         2/height,   1],
                        [0,         0,          1]

                    ]
        
        matPPC = np.dot(np.dot(matTrans, matRot), matScale)
        self.ppcMatrix = matPPC

    def applyPPCmatrixOne(self, obj):
        if obj.type == "Point":
            P = [obj.x, obj.y, 1]
            (X,Y,W) = np.dot(P, self.ppcMatrix)
            obj.cn_x = X
            obj.cn_y = Y
        elif obj.type == "Line":
            P1 = [obj.p1.x, obj.p1.y, 1]
            P2 = [obj.p2.x, obj.p2.y, 1]
            (X1, Y1, W1) = np.dot(P1, self.ppcMatrix)
            (X2, Y2, W2) = np.dot(P2, self.ppcMatrix)
            obj.p1.cn_x = X1
            obj.p1.cn_y = Y1
            obj.p2.cn_x = X2
            obj.p2.cn_y = Y2
            print("N: {}, {}".format(obj.p1.x, obj.p1.y))
            print("PPC: {}, {}".format(obj.p1.cn_x, obj.p1.cn_y))
        elif obj.type == "Polygon":
            for p in obj.points:
                P = (p.x, p.y, 1)
                (X,Y,W) = np.matmul(P, self.ppcMatrix)
                p.cn_x = X
                p.cn_y = Y

    def applyPPCmatrixAll(self):
        for obj in self.displayFile:
            self.applyPPCmatrixOne(obj)

    def applyPPCmatrixWindow(self):
        p1 = Point(self.cgWindow.xMin, self.cgWindow.yMin)
        p2 = Point(self.cgWindow.xMin, self.cgWindow.yMax)
        p3 = Point(self.cgWindow.xMax, self.cgWindow.yMax)
        p4 = Point(self.cgWindow.xMax, self.cgWindow.yMin)
        temp = Wireframe([p1, p2, p3, p4])
        self.applyPPCmatrixOne(temp)

        xs = []
        ys = []
        for point in temp.points:
            xs.append(point.cn_x)
            ys.append(point.cn_y)

        xmin = min(xs)
        ymin = min(ys)
        xmax = max(xs)
        ymax = max(ys)

        """ self.cgWindowPPC.xMin = temp.points[0].cn_x
        self.cgWindowPPC.yMin = temp.points[0].cn_y
        self.cgWindowPPC.xMax = temp.points[2].cn_x
        self.cgWindowPPC.yMax = temp.points[2].cn_y """

        self.cgWindowPPC.xMin = xmin
        self.cgWindowPPC.yMin = ymin
        self.cgWindowPPC.xMax = xmax
        self.cgWindowPPC.yMax = ymax

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
        degree = np.deg2rad(degree)
        centroInicial = self.find_center(obj)
        print(toOrigin)
        print(toObject)
        print(toPoint)
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
            print(obj.p1.x)
            obj.p1.y = Y1
            print(obj.p1.y)
            obj.p2.x = X2
            print(obj.p2.x)
            obj.p2.y = Y2
            print(obj.p2.y)
            
            print("ANTES DE SAIR DA ROTAÇÃO: ")
            print("{}, {}\n{}, {}".format(obj.p1.x, obj.p1.y, obj.p2.x, obj.p2.y))
            print("------------------")

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

    def zoomViewportOut(self):
        #clamp()
        self.cgWindow.xMax += 10
        self.cgWindow.xMin -= 10
        self.cgWindow.yMax += 10
        self.cgWindow.yMin -= 10
        self.makePPCmatrix()
        self.applyPPCmatrixWindow()
        self.drawAll()

    def zoomViewportIn(self):
        #clamp()
        self.cgWindow.xMax -= 10
        self.cgWindow.xMin += 10
        self.cgWindow.yMax -= 10
        self.cgWindow.yMin += 10
        self.makePPCmatrix()
        self.applyPPCmatrixWindow()
        self.drawAll()

    def panRight(self):
        v = [1, 0]
        ang = np.deg2rad(self.windowAngle)
        x = np.cos(ang)*v[0] - np.sin(ang)*v[1]
        y = np.sin(ang)*v[0] + np.cos(ang)*v[1]
        print([x, y])
        self.cgWindow.xMax += x * 10
        self.cgWindow.xMin += x * 10
        self.cgWindow.yMax += y * 10
        self.cgWindow.yMin += y * 10
        self.makePPCmatrix()
        self.applyPPCmatrixWindow()
        self.drawAll()

    def panLeft(self):
        v = [-1, 0]
        ang = np.deg2rad(self.windowAngle)
        x = np.cos(ang)*v[0] - np.sin(ang)*v[1]
        y = np.sin(ang)*v[0] + np.cos(ang)*v[1]
        print([x, y])
        self.cgWindow.xMax += x * 10
        self.cgWindow.xMin += x * 10
        self.cgWindow.yMax += y * 10
        self.cgWindow.yMin += y * 10
        self.makePPCmatrix()
        self.applyPPCmatrixWindow()
        self.drawAll()
    
    def panUp(self):
        #PROVISORIO
        v = [0, 1]
        ang = np.deg2rad(self.windowAngle)
        x = np.cos(ang)*v[0] - np.sin(ang)*v[1]
        y = np.sin(ang)*v[0] + np.cos(ang)*v[1]
        print([x, y])
        self.cgWindow.xMax += x * 10
        self.cgWindow.xMin += x * 10
        self.cgWindow.yMax += y * 10
        self.cgWindow.yMin += y * 10
        self.makePPCmatrix()
        self.applyPPCmatrixWindow()
        self.drawAll()

    def panDown(self):
        v = [0, -1]
        ang = np.deg2rad(self.windowAngle)
        x = np.cos(ang)*v[0] - np.sin(ang)*v[1]
        y = np.sin(ang)*v[0] + np.cos(ang)*v[1]
        print([x, y])
        self.cgWindow.xMax += x * 10
        self.cgWindow.xMin += x * 10
        self.cgWindow.yMax += y * 10
        self.cgWindow.yMin += y * 10
        self.makePPCmatrix()
        self.applyPPCmatrixWindow()
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

        self.windowAngle = 0

        self.makePPCmatrix()
        self.applyPPCmatrixWindow()
        self.drawAll()

    def loadObjs(self):
        newObjs = self.descObj.load("teste.obj")
        for obj in newObjs:
            self.displayFile.append(obj)
        self.drawAll()

    def printalista(self):
        print(self.objectList.currentRow())
    #Fazer um método pra dar self.painter.end() no término do programa
