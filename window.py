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
        self.wSize = [0, 0, 400, 300]
        self.windowAngle = 0
        
        self.cgViewport = Container(self.vpSize[0], self.vpSize[1], self.vpSize[2], self.vpSize[3])
        self.cgWindow = Container(self.wSize[0], self.wSize[1], self.wSize[2], self.wSize[3])
        self.cgWindowPPC = Container(-1,-1,1,1)
        self.cgSubcanvas = Container(20, 20, 380, 380)
        
        self.ppcMatrix =    [   [0, 0, 0],
                                [0, 0, 0],
                                [0, 0, 0]
                            ]
        
        self.descObj = DescritorOBJ()
        
        self.makePPCmatrix()
        self.applyPPCmatrixWindow()

        self.drawBorder()

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

    def drawBorder(self):
        self.pen = QtGui.QPen(Qt.red)
        self.pen.setWidth(5)
        self.painter.setPen(self.pen)

        self.painter.drawLine(20, 20, 380, 20)
        self.painter.drawLine(380, 20, 380, 380)
        self.painter.drawLine(380, 380, 20, 380)
        self.painter.drawLine(20, 380, 20, 20)

    def drawOne(self, object):
        self.applyPPCmatrixOne(object)
        self.pen = QtGui.QPen(QtGui.QColor(object.color[0], object.color[1], object.color[2], 255))
        self.pen.setWidth(5)
        self.painter.setPen(self.pen)
        
        if object.type == "Point":
            (x, y) = self.viewportTransformation(object)
            if self.pointClipping(x,y):
                self.painter.drawPoint(x, y)
        elif object.type == "Line":
            (x1, y1) = self.viewportTransformation(object.p1)
            (x2,y2) = self.viewportTransformation(object.p2)
            print(f"ponto 1 ({x1}, {y1})")
            print(f"ponto 2 ({x2}, {y2})")
            if self.csCheck.isChecked():
                clipRes = self.csLineClipping(x1, y1, x2, y2)
            else:
                clipRes = self.lbLineClipping(x1, y1, x2, y2)
            print(clipRes)
            if clipRes[0]:
                self.painter.drawLine(int(clipRes[1]), int(clipRes[2]), int(clipRes[3]), int(clipRes[4]))
            #self.painter.drawLine(x1, y1, x2, y2)
        elif object.type == "Polygon":
            ps = []
            fill_p = []
            for p in object.points:
                ps.append(self.viewportTransformation(p))

  
            ok, newobj = self.Waclippig(ps)
            nps = newobj[0]
            
            if not ok: return

            for i in range(1, len(ps)):
                self.painter.drawLine(int(nps[i-1][0]), int(nps[i-1][1]), int(nps[i][0]), int(nps[i][1]))
            
                if nps[-1] == nps[:-1][-1]: return 
                self.painter.drawLine(int(nps[-1][0]), int(nps[-1][1]), int(nps[0][0]), int(nps[0][1]))
            
                if object.filled:
                    fill_p.append((int(nps[i-1][0]), int(nps[i-1][1])))

                if fill_p:
                    # Create QPoints just to use filling primitive from pyqt
                    polygon = QtGui.QPolygonF()
                    for point in fill_p:
                        new_point = QtCore.QPointF(point[0], point[1])
                        polygon.append(new_point)
                    path = QtGui.QPainterPath()
                    path.addPolygon(polygon)
                    self.painter.setBrush(QtGui.QColor(*object.color))
                    self.painter.drawPath(path)
                
            

            print("LEN COMPARE")
            print(ps)
            print(nps)

    def drawAll(self):
        #Limpa
        self.mainLabel.pixmap().fill(Qt.white)

        #Borda
        self.drawBorder()

        #Desenha tudo
        for object in self.displayFile:
            print(object)
            self.drawOne(object)
        self.update()

    def pointClipping(self, x, y):
        xIn = False
        yIn = False

        if x <= self.cgSubcanvas.xMax and self.cgSubcanvas.xMin <= x:
            xIn = True

        if y <= self.cgSubcanvas.yMax and self.cgSubcanvas.yMin <= y:
            yIn = True

        print(x, y, self.cgSubcanvas.xMax, self.cgSubcanvas.xMin)
        return xIn and yIn
    
    def rcFinder(self, x, y):
        res = 0
        if y > self.cgSubcanvas.yMax:
            res += 8
            #Cima
        elif y < self.cgSubcanvas.yMin:
            #baixo
            res += 4

        if x < self.cgSubcanvas.xMin:
            #Esquerda
            res += 1
        elif x > self.cgSubcanvas.xMax:
            #Direita
            res += 2
        return res

    def csLineClipping(self, ox1, oy1, ox2, oy2):
        #RC[0] = Acima      (8)
        #RC[1] = Abaixo     (4)
        #RC[2] = Direita    (2)
        #RC[3] = Esquerda   (1)

        print("CLIPPANDO POR COHEN SUTHERLAND")

        x1 = ox1
        y1 = oy1

        x2 = ox2
        y2 = oy2

        rc1 = 0
        rc2 = 0
        
        rc1 = rc1 | self.rcFinder(x1, y1)
        rc2 = rc2 | self.rcFinder(x2, y2)

        while True:
            if rc1 == rc2 and rc1 == 0:
                return (True, x1, y1, x2, y2)
            elif rc1 & rc2 != 0:
                return (False, 0, 0, 0, 0)
            
            intX = 0
            intY = 0

            if rc1 != 0:
                rcMax = rc1
            else:
                rcMax = rc2

            if rcMax & 8  == 8:
                intX = x1 + (x2 - x1) * (self.cgSubcanvas.yMax - y1) / (y2 - y1)
                intY = self.cgSubcanvas.yMax
            elif rcMax & 4 == 4:
                intX = x1 + (x2 - x1) * (self.cgSubcanvas.yMin - y1) / (y2 - y1)
                intY = self.cgSubcanvas.yMin
            elif rcMax & 2 == 2:
                intY = y1 + (y2 - y1) * (self.cgSubcanvas.xMax - x1) / (x2 - x1)
                intX = self.cgSubcanvas.xMax
            elif rcMax & 1 == 1:
                intY = y1 + (y2 - y1) * (self.cgSubcanvas.xMin - x1) / (x2 - x1)
                intX = self.cgSubcanvas.xMin

            if rcMax == rc1:
                x1 = intX
                y1 = intY
                rc1 = self.rcFinder(x1, y1)
            else:
                x2 = intX
                y2 = intY
                rc2 = self.rcFinder(x2, y2)

    def lbLineClipping(self, ox1, oy1, ox2, oy2):
        print("CLIPPANDO POR LIANG BARSKY")
        
        x1 = ox1
        y1 = oy1
        x2 = ox2
        y2 = oy2

        p1 = -(x2 - x1)
        p2 = -p1
        p3 = -(y2 - y1)
        p4 = -p3

        q1 = x1 - self.cgSubcanvas.xMin
        q2 = self.cgSubcanvas.xMax - x1
        q3 = y1 - self.cgSubcanvas.yMin
        q4 = self.cgSubcanvas.yMax - y1

        ps = [p1, p2, p3, p4]
        qs = [q1, q2, q3, q4]

        #Checa fora dos limites
        pcond = False
        qcond = False
        for p in ps:
            if p == 0:
                pcond = True
                break
        if pcond:
            for q in qs:
                if q < 0:
                    qcond = True
        if qcond:
            print("qcond foi")
            return (False, 0, 0, 0, 0)
        
        #Contas
        negs = []
        for i in range(4):
            if ps[i] < 0:
                negs.append((ps[i], i))

        poss = []
        for i in range(4):
            if ps[i] > 0:
                poss.append((ps[i], i))

        #R negativos
        rns = []
        for neg in negs:
            rns.append(qs[neg[1]]/neg[0])

        #R positivos
        rps = []
        for pos in poss:
            rps.append(qs[pos[1]]/pos[0])

        #N sei que simbolo eh aquele ent vai U
        u1 = max(0, max(rns))
        u2 = min(1, min(rps))
        print("u1: {}".format(u1))
        print("u2: {}".format(u1))


        #Saiu
        if u1 > u2:
            print("des u foi")
            return (False, 0, 0, 0, 0)
        
        #interseccoes
        ix1 = x1 + u1 * p2
        iy1 = y1 + u1 * p4

        ix2 = x1 + u2 * p2
        iy2 = y1 + u2 * p4

        return (True, ix1, iy1, ix2, iy2)
    
    def w_a_get_window_index(self, window_vertices, point, code):
        x, y = point
        # The index from window vertices list must be the
        # right before the next window vertice
        if x == self.cgSubcanvas.xMax:
            # Right, so right bottom
            index = window_vertices.index(
                ((self.cgSubcanvas.xMax, self.cgSubcanvas.yMin), 0))
            window_vertices.insert(index, (point, code))
        if x == self.cgSubcanvas.xMin:
            # Left, so left top
            index = window_vertices.index(
                ((self.cgSubcanvas.xMin, self.cgSubcanvas.yMax), 0))

            window_vertices.insert(index, (point, code))
        if y == self.cgSubcanvas.yMax:
            # Top, so right top
            index = window_vertices.index(
                ((self.cgSubcanvas.xMax, self.cgSubcanvas.yMax), 0))
            window_vertices.insert(index, (point, code))
        if y == self.cgSubcanvas.yMin:
            # Bottom, so left bottom
            index = window_vertices.index(
                ((self.cgSubcanvas.xMin, self.cgSubcanvas.yMin), 0))
            window_vertices.insert(index, (point, code))
        return window_vertices


    def waLimites(self, points):
            inside = []
            for p in points:
                if (p[0] >= self.cgSubcanvas.xMin
                    and p[1] >= self.cgSubcanvas.yMin) and (
                    p[0] <= self.cgSubcanvas.xMax
                    and p[1] <= self.cgSubcanvas.yMax):
                    inside.append(p)

            return inside

    def Waclippig(self, coordenadas):
        print("COORDENADAS INICIASIS")
        print(coordenadas)
        pontosDentro = self.waLimites(coordenadas)
        if not pontosDentro:
            return False, [None]
        
        win_vers = [((self.cgSubcanvas.xMin, self.cgSubcanvas.yMax), 0), 
                    ((self.cgSubcanvas.xMax, self.cgSubcanvas.yMax), 0), 
                    ((self.cgSubcanvas.xMax, self.cgSubcanvas.yMin), 0), 
                    ((self.cgSubcanvas.xMin, self.cgSubcanvas.yMin), 0)]
        obj_vertices = [(list(c), 0) for c in coordenadas]

        total_pontos = len(coordenadas)
        pontos_inseridos = []

        for i in range(total_pontos):
            p0 = list(coordenadas[i])
            p1 = list(coordenadas[(i + 1) % total_pontos])
            
            np0 = [None, None]
            np1 = [None, None]

            visivel, np0[0], np0[1], np1[0], np1[1] = self.csLineClipping(
                p0[0], p0[1], p1[0], p1[1])
            if visivel:
                if np1 != p1:
                    point_idx = obj_vertices.index((p0, 0)) + 1
                    obj_vertices.insert(point_idx, (np1, 2))
                    win_vers = self.w_a_get_window_index(win_vers, np1, 2)

                if np0 != p0:
                    point_idx = obj_vertices.index((p0, 0)) + 1
                    obj_vertices.insert(point_idx, (np0, 1))
                    pontos_inseridos.append((np0, 1))
                    win_vers = self.w_a_get_window_index(win_vers, np0, 1)
    
        poligonos_novos = []
        pontos_novos = []
        if pontos_inseridos != []:
            while pontos_inseridos != []:
                ref = pontos_inseridos.pop(0)
                rf_p, _ = ref 
                inside_points = [rf_p]
                point_idx = obj_vertices.index(ref) + 1
                pontos_novos.append(ref)

                obj_len = len(obj_vertices)
                for aux_index in range(obj_len):
                    (p, c) = obj_vertices[(point_idx + aux_index) % obj_len]
                    pontos_novos.append((p, c))
                    inside_points.append(p)
                    if c != 0:
                        break 

                ultimo_ponto = pontos_novos[-1]
                point_idx = win_vers.index(ultimo_ponto)
                win_len = len(win_vers)
                for aux_index in range(win_len):
                    (p, c) = win_vers[(point_idx + aux_index) % win_len]
                    pontos_novos.append((p, c))
                    inside_points.append(p)
                    if c != 0:
                        break

                poligonos_novos.append(inside_points)
            coordenada = poligonos_novos
        else:
            coordenada = [coordenadas]
        return True, coordenada
                    

    #FUNCOES DE JANELA

    def novoPontoWindow(self):
        novoPontoDialog = UiPonto()
        if novoPontoDialog.exec_() and novoPontoDialog.xValue.text() and novoPontoDialog.yValue.text():
            x = int(novoPontoDialog.xValue.text())
            y = int(novoPontoDialog.yValue.text())
            novoPonto = Point(x, y, "Ponto {}".format(self.indexes[0]), 0, 0)
            self.displayFile.append(novoPonto)
            self.indexes[0] += 1
            self.objectList.addItem(novoPonto.name)
            if novoPontoDialog.rValue.text() and novoPontoDialog.gValue.text() and novoPontoDialog.bValue.text():
                novoPonto.color = (int(novoPontoDialog.rValue.text()), int(novoPontoDialog.gValue.text()), int(novoPontoDialog.bValue.text()), 255)
            else:
                novoPonto.color = (0,0,0,255)
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
                newLine.color = ((int(novaLinhaDialog.rValue.text()), int(novaLinhaDialog.gValue.text()), int(novaLinhaDialog.bValue.text()), 255))
            else:
                newLine.color = (0,0,0,255)
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
            print(newPoly)
            self.displayFile.append(newPoly)
            self.indexes[2] += 1
            self.objectList.addItem(newPoly.name)
            if novoPoligonoDialog.rValue.text() and novoPoligonoDialog.gValue.text() and novoPoligonoDialog.bValue.text():
                newPoly.color = ((int(novoPoligonoDialog.rValue.text()), int(novoPoligonoDialog.gValue.text()), int(novoPoligonoDialog.bValue.text()), 255))
            else:
                newPoly.color = (0,0,0,255)
            if novoPoligonoDialog.fillCheckBox.isChecked():
                newPoly.filled = True
                print('prenchjdo = true')
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
        if self.cgWindow.xMax - 10 > self.cgWindow.xMin + 10 and self.cgWindow.yMax - 10 > self.cgWindow.yMin + 10:
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
            self.objectList.addItem(obj.name)
        self.drawAll()

    def printalista(self):
        print(self.objectList.currentRow())
    #Fazer um método pra dar self.painter.end() no término do programa
