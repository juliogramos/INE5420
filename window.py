import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import Qt
import numpy as np

from dataclasses import dataclass

from numpy._typing import _256Bit
from object import BSplineCurve, Point, Line, Wireframe, Curve2D, Point3D, Object3D
from novoPonto import UiPonto
from novaLinha import UiLinha
from novoPoligono import UiPoligono
from novaCurva import UiCurva
from novaBSCurva import UiBSCurva
from novoPonto3D import UiPonto3D
from novoPoligono3D import UiPoligono3D

from transformacao import UiTransforma
from rotwindow import UiRotWin

from transformacao3d import UiTransforma3D

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
        #Ponto, Linha, Poligono, Curva, Spline, Ponto3D, Objeto3D
        self.indexes = [1, 1, 1, 1, 1, 1, 1]
        self.displayFile = []

        self.vpSize = [0, 0, 400, 400]
        self.wSize = [0, 0, 400, 300]
        self.windowAngle = [0, 0, 0] #X, Y, Z
        
        self.projmode = "ortogonal" #ou "perspectiva"
        self.perspd = 100
        
        self.cgViewport = Container(self.vpSize[0], self.vpSize[1], self.vpSize[2], self.vpSize[3])
        self.cgWindow = Container(self.wSize[0], self.wSize[1], self.wSize[2], self.wSize[3])
        self.cgWindowPPC = Container(-1,-1,1,1)
        self.cgSubcanvas = Container(20, 20, 380, 380)
        
        self.ppcMatrix =    [   [0, 0, 0],
                                [0, 0, 0],
                                [0, 0, 0]
                            ]
        
        self.ppcMatrix3D =      [   [0, 0, 0, 0],
                                    [0, 0, 0, 0],
                                    [0, 0, 0, 0],
                                    [0, 0, 0, 0]
                                ]
        
        self.descObj = DescritorOBJ()
        
        self.makePPCmatrix()
        self.applyPPCmatrixWindow()

        self.drawBorder()

        self.cuboteste()
    

    def viewportTransformation(self, point):
        #xvp = (point.cn_x - self.cgWindow.xMin)/(self.cgWindow.xMax - self.cgWindow.xMin) * (self.cgViewport.xMax - self.cgViewport.xMin) 
        #yvp = (1 - ((point.cn_y - self.cgWindow.yMin)/(self.cgWindow.yMax - self.cgWindow.yMin))) * (self.cgViewport.yMax - self.cgViewport.yMin)
        xvp = (point.cn_x - self.cgWindowPPC.xMin)/(self.cgWindowPPC.xMax - self.cgWindowPPC.xMin) * (self.cgViewport.xMax - self.cgViewport.xMin) 
        yvp = (1 - ((point.cn_y - self.cgWindowPPC.yMin)/(self.cgWindowPPC.yMax - self.cgWindowPPC.yMin))) * (self.cgViewport.yMax - self.cgViewport.yMin)
        print(xvp)
        print(yvp)
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
        self.newCurve.clicked.connect(self.novaCurvaWindow)
        self.newBSCurve.clicked.connect(self.novaBSplineCurvaWindow)
        
        self.newPoint3D.clicked.connect(self.novoPonto3DWindow)
        self.newPoligon3D.clicked.connect(self.novoPoligono3DWindow)

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
        
        self.perspSlider.valueChanged.connect(self.perspChange)
        self.projOrt.toggled.connect(self.drawAll)
        self.projPersp.toggled.connect(self.drawAll)

    def drawBorder(self, color=Qt.red):
        self.pen = QtGui.QPen(color)
        self.pen.setWidth(5)
        self.painter.setPen(self.pen)
        points = [(20, 20), (20, 380), (380, 20), (380, 380)]

        polygon = QtGui.QPolygonF()
        for point in points:
            new_point = QtCore.QPointF(point[0], point[1])
            
            polygon.append(new_point)
        path = QtGui.QPainterPath()
        path.addPolygon(polygon)
        self.painter.setBrush(QtGui.QColor(Qt.red))
        self.painter.drawLine(polygon[0], polygon[1])
        self.painter.drawLine(polygon[0], polygon[2])
        self.painter.drawLine(polygon[1], polygon[3])
        self.painter.drawLine(polygon[2], polygon[3])

        print("desenhou borda")
        
    def drawOne(self, object):
        self.pen = QtGui.QPen(QtGui.QColor(object.color[0], object.color[1], object.color[2], 255))
        self.pen.setWidth(5)
        self.painter.setPen(self.pen)
        
        if object.dimension == 2:
            self.drawOne2D(object)
        else:
            self.drawOne3D(object)
                
    def drawOne2D(self, object):
        print("DRAW 2D")
        self.applyPPCmatrixOne(object)
        
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

            for i in range(1, len(nps)):
                self.painter.drawLine(int(nps[i-1][0]), int(nps[i-1][1]), int(nps[i][0]), int(nps[i][1]))
            
            
                if object.filled:
                    fill_p.append((int(nps[i-1][0]), int(nps[i-1][1])))

            if object.filled:
                fill_p.append((int(nps[-1][0]), int(nps[-1][1])))
                print("FILLP")
                print(fill_p)

            if fill_p:
                # Create QPoints just to use filling primitive from pyqt
                polygon = QtGui.QPolygonF()
                for point in fill_p:
                    new_point = QtCore.QPointF(point[0], point[1])

                    polygon.append(new_point)
                #if polygon[-1] == polygon[:-1][-1]: polygon.removeLast()
                path = QtGui.QPainterPath()
                path.addPolygon(polygon)
                self.painter.setBrush(QtGui.QColor(*object.color))
                self.painter.drawPath(path)
                
            
            print("LEN COMPARE")
            print(ps)
            print(nps)
            if nps[-1] == nps[:-1][-1]: return 
            self.painter.drawLine(int(nps[-1][0]), int(nps[-1][1]), int(nps[0][0]), int(nps[0][1]))

        elif object.type == "Curve":
            ps = []
            for p in object.points:
                ps.append(self.viewportTransformation(p))
            nps = self.curveClipping(ps)
            if nps:
                print("LEN BELOW")
                print(len(nps))
                for i in range(1, len(nps)):
                    self.painter.drawLine(int(nps[i-1][0]), int(nps[i-1][1]), int(nps[i][0]), int(nps[i][1]))
                
    def drawOne3D(self, object):
        print("DRAW 3D")
        self.applyPPCmatrixOne(object)
        
        if object.type == "Point3D":
            (x, y) = self.viewportTransformation(object)
            if self.pointClipping(x,y):
                self.painter.drawPoint(x, y)
                
        elif object.type == "Polygon3D":
            ps = []
            for p in object.points:
                ps.append(self.viewportTransformation(p))

            nedges = []
            for e in object.edges:
                x1 = ps[e[0]][0]
                y1 = ps[e[0]][1]
                x2 = ps[e[1]][0]
                y2 = ps[e[1]][1]
                print(x1, y1, x2, y2)
                ok, nx1, ny1, nx2, ny2 = self.csLineClipping(x1, y1, x2, y2)
                if ok:
                    nedges.append(((nx1, ny1),(nx2, ny2)))

            for (p1, p2) in nedges:
                self.painter.drawLine(int(p1[0]), int(p1[1]), int(p2[0]), int(p2[1]))
        

    def drawAll(self):
        #Limpa
        self.mainLabel.pixmap().fill(Qt.white)

        #Borda
        self.drawBorder()

        #Desenha tudo
        for object in self.displayFile:
            print(object)
            self.drawOne(object)
        
            self.drawBorder()
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
            if rcMax & 4 == 4:
                intX = x1 + (x2 - x1) * (self.cgSubcanvas.yMin - y1) / (y2 - y1)
                intY = self.cgSubcanvas.yMin
            if rcMax & 2 == 2:
                intY = y1 + (y2 - y1) * (self.cgSubcanvas.xMax - x1) / (x2 - x1)
                intX = self.cgSubcanvas.xMax
            if rcMax & 1 == 1:
                intY = y1 + (y2 - y1) * (self.cgSubcanvas.xMin - x1) / (x2 - x1)
                intX = self.cgSubcanvas.xMin

            if rcMax == rc1:
                x1 = intX
                y1 = intY
                rc1 = 0
                rc1 = self.rcFinder(x1, y1)
            else:
                x2 = intX
                y2 = intY
                rc2 = 0
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

            print("PONTOS INSERIDOS")
            print(pontos_inseridos)
    
        poligonos_novos = []
        pontos_novos = []
        if pontos_inseridos != []:
            while pontos_inseridos != []:
                ref = pontos_inseridos.pop(0)
                rf_p, _ = ref 
                print()
                print(ref, rf_p)
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
                print(ultimo_ponto)
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

        print("COORDENADA")
        print(coordenada)
        return True, coordenada
                    
    def curveClipping(self, points):
        clipPoints = []
        started = False
        for i in range(1, len(points)):
            p1 = points[i-1]
            p2 = points[i]

            x1 = p1[0]
            y1 = p1[1]

            x2 = p2[0]
            y2 = p2[1]

            clipped = self.csLineClipping(x1, y1, x2, y2)
            if clipped[0]:
                if started == False: started = True
                clipPoints.append((clipped[1], clipped[2]))
                clipPoints.append((clipped[3], clipped[4]))
            else:
                if started: break

        return clipPoints

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

    def novaCurvaWindow(self):
        #PONTOS PRO TESTE
        """ ps = [Point(110, 110, "P1"),
                Point(120, 130, "P2"),
                Point(130, 100, "P3"),
                Point(140, 110, "P4"),
                Point(150, 120, "P5"),
                Point(140, 140, "P6"),
                Point(160, 140, "P7"),
                Point(170, 140, "P8"),
                Point(160, 120, "P9"),
                Point(170, 110, "P10") 
                ] """
        novaCurvaDialog = UiCurva()
        if novaCurvaDialog.exec_() and len(novaCurvaDialog.listaPontos) >= 4 and novaCurvaDialog.precisao.text():
            
            print("Entrou curva")
            ps = novaCurvaDialog.curveList
            precisao = float(novaCurvaDialog.precisao.text())
            cont = 0

            if novaCurvaDialog.c1.isChecked(): cont = 1
            elif novaCurvaDialog.c2.isChecked(): cont = 2
            elif novaCurvaDialog.c3.isChecked(): cont = 3
            if cont == 0 and len(novaCurvaDialog.listaPontos) % 4 != 0:
                self.status.addItem("Número de pontos deve ser um múltiplo de 4!")
                self.update()
                return
            elif cont == 1 and (len(novaCurvaDialog.listaPontos) - 4) % 3 != 0:
                self.status.addItem("Número de pontos deve ser 4 + um múltiplo de 3!")
                self.update()
                return
            elif cont == 2 and (len(novaCurvaDialog.listaPontos) - 4) % 2 != 0:
                self.status.addItem("Número de pontos deve ser 4 + um múltiplo de 2!")
                self.update()
                return

            curvePoints = self.makeCurve(ps, precisao, cont)
            newCurve = Curve2D(curvePoints, "Curva {}".format(self.indexes[3]))
            self.displayFile.append(newCurve)
            self.indexes[3] += 1
            self.objectList.addItem(newCurve.name)
            if novaCurvaDialog.rValue.text() and novaCurvaDialog.gValue.text() and novaCurvaDialog.bValue.text():
                newCurve.color = ((int(novaCurvaDialog.rValue.text()), int(novaCurvaDialog.gValue.text()), int(novaCurvaDialog.bValue.text()), 255))
            else:
                newCurve.color = (0,0,0,255)
            self.drawOne(newCurve)
            self.status.addItem("Curva adicionado com sucesso.")
        else:
            self.status.addItem("Falha ao adicionar curva.")
        self.update()

    def novaBSplineCurvaWindow(self):
            #PONTOS PRO TESTE
            """ ps = [Point(110, 110, "P1",
                    Point(120, 130, "P2"),
                    Point(130, 100, "P3"),
                    Point(140, 110, "P4"),
                    Point(150, 120, "P5"),
                    Point(140, 140, "P6"),
                    Point(160, 140, "P7"),
                    Point(170, 140, "P8"),
                    Point(160, 120, "P9"),
                    Point(170, 110, "P10") 
                    ] """
            novaSPCurvaDialog = UiBSCurva()
            if novaSPCurvaDialog.exec_() and len(novaSPCurvaDialog.listaPontos) >= 4 and novaSPCurvaDialog.precisao.text():
                
                print("Entrou curva")
                ps = novaSPCurvaDialog.curveList
                precisao = float(novaSPCurvaDialog.precisao.text())
                
                curvePoints = self.makeBSCurve(ps, precisao)
                print("CURVEPOINTS:")
                for p in curvePoints:
                    print(p)
                newCurve = BSplineCurve(curvePoints, "Curva {}".format(self.indexes[4]))
                self.displayFile.append(newCurve)
                self.indexes[4] += 1
                self.objectList.addItem(newCurve.name)
                if novaSPCurvaDialog.rValue.text() and novaSPCurvaDialog.gValue.text() and novaSPCurvaDialog.bValue.text():
                    newCurve.color = ((int(novaSPCurvaDialog.rValue.text()), int(novaSPCurvaDialog.gValue.text()), int(novaSPCurvaDialog.bValue.text()), 255))
                else:
                    newCurve.color = (0,0,0,255)
                self.drawOne(newCurve)
                self.status.addItem("Curva adicionado com sucesso.")
            else:
                self.status.addItem("Falha ao adicionar curva.")
            self.update()


    def getBlending(self, t):
        return [(1 - t) ** 3, 3 * t * ((1 - t) ** 2), 3 * (t ** 2) * (1 - t), t ** 3]

    def makeCurve(self, polyList, precisao, cont):
        #CONTINUIDADE 1 (mudar condição do exec se quiser outra continuidade)
        # ou mudar pra especificar na criacao talvez
        prelistsX = []
        prelistsY = []
        newlistsX = []
        newlistsY = []
        newCoords = []
        
        step = 0
        if cont == 0: step = 4
        elif cont == 1: step = 3
        elif cont == 2: step = 2
        elif cont == 3: step = 1

        for i in range(3, len(polyList), step):
            prelistsX.append([polyList[i-3].x, polyList[i-2].x, polyList[i-1].x, polyList[i].x])
            prelistsY.append([polyList[i-3].y, polyList[i-2].y, polyList[i-1].y, polyList[i].y])

        for i in range(len(prelistsX)):
            t = 0
            while t < 1:
                newlistsX.append(np.dot(self.getBlending(t), prelistsX[i]))
                newlistsY.append(np.dot(self.getBlending(t), prelistsY[i]))
                t += precisao
            newlistsX.append(np.dot(self.getBlending(1), prelistsX[i]))
            newlistsY.append(np.dot(self.getBlending(1), prelistsY[i]))
        
        coords = list(zip(newlistsX, newlistsY))
        ps = []
        for c in coords:
            ps.append(Point(c[0], c[1]))
        return ps

    def calculate_bspline_param(self, points, precisao):
        MBS = np.array(
        [
            [-1 / 6, 1 / 2, -1 / 2, 1 / 6],
            [1 / 2, -1, 1 / 2, 0],
            [-1 / 2, 0, 1 / 2, 0],
            [1 / 6, 2 / 3, 1 / 6, 0],
        ]
        )

        GBS_x = []
        GBS_y = []
        for point in points:
            GBS_x.append(point.x)
            GBS_y.append(point.y)

        GBS_x = np.array([GBS_x]).T 
        coeff_x = MBS.dot(GBS_x).T[0]
        aX, bX, cX, dX = coeff_x
        init_diff_x = [
               dX,
                aX * (precisao ** 3) + bX * (precisao ** 2) + cX * precisao,
                6 * aX * (precisao ** 3) + 2 * bX * (precisao ** 2),
                6 * aX * (precisao ** 3)
                    ]

        GBS_y = np.array([GBS_y]).T 
        coeff_y = MBS.dot(GBS_y).T[0]
        aY, bY, cY, dY = coeff_y
        init_diff_y = [
               dY,
                aY * (precisao ** 3) + bY * (precisao ** 2) + cY * precisao,
                6 * aY * (precisao ** 3) + 2 * bY * (precisao ** 2),
                6 * aY * (precisao ** 3)
                    ]
        return init_diff_x, init_diff_y

    def makeBSCurve(self, polyList, precisao):
        spline_points = []
        iterations = int(1/precisao)
        num_points = len(polyList)
        min_points = 4 

        for i in range(0, num_points):
            upper_bound = i + min_points

            if upper_bound > num_points:
                break
            points = polyList[i:upper_bound]

            
            delta_x, delta_y = self.calculate_bspline_param(points, precisao)
            x = delta_x[0]
            y = delta_y[0]
            print("DELTA X")
            print(delta_x)
            print("DELTA y")
            print(delta_y)
            spline_points.append(Point(x, y))
            for _ in range(0, iterations):
                x += delta_x[1]
                delta_x[1] += delta_x[2] 
                delta_x[2] += delta_x[3]
                
                y += delta_y[1]
                delta_y[1] += delta_y[2] 
                delta_y[2] += delta_y[3]

                spline_points.append(Point(x, y))
        print("sp points")
        print(spline_points)
        return spline_points
    
    def novoPonto3DWindow(self):
        novoPontoDialog = UiPonto3D()
        if novoPontoDialog.exec_() and (
            novoPontoDialog.xValue.text() and 
            novoPontoDialog.yValue.text() and
            novoPontoDialog.zValue.text()):
            
            x = int(novoPontoDialog.xValue.text())
            y = int(novoPontoDialog.yValue.text())
            z = int(novoPontoDialog.zValue.text())
            
            novoPonto = Point3D(x, y, z, "Ponto 3D{}".format(self.indexes[5]), 0, 0)
            self.displayFile.append(novoPonto)
            self.indexes[5] += 1
            self.objectList.addItem(novoPonto.name)
            if novoPontoDialog.rValue.text() and novoPontoDialog.gValue.text() and novoPontoDialog.bValue.text():
                novoPonto.color = (int(novoPontoDialog.rValue.text()), int(novoPontoDialog.gValue.text()), int(novoPontoDialog.bValue.text()), 255)
            else:
                novoPonto.color = (0,0,0,255)
            self.drawOne(novoPonto)

            self.status.addItem("Ponto 3D adicionado com sucesso.")
        else:
            self.status.addItem("Falha ao adicionar ponto.")

        self.update()
        
    def novoPoligono3DWindow(self):
        novoPoligonoDialog = UiPoligono3D()
        if novoPoligonoDialog.exec_() and novoPoligonoDialog.polyList and novoPoligonoDialog.edgeList:
            newPoly = Object3D(novoPoligonoDialog.polyList, 
                               novoPoligonoDialog.edgeList,
                               "Polígono {}".format(self.indexes[2]))
            print(newPoly)
            self.displayFile.append(newPoly)
            self.indexes[2] += 1
            self.objectList.addItem(newPoly.name)
            if novoPoligonoDialog.rValue.text() and novoPoligonoDialog.gValue.text() and novoPoligonoDialog.bValue.text():
                newPoly.color = ((int(novoPoligonoDialog.rValue.text()), int(novoPoligonoDialog.gValue.text()), int(novoPoligonoDialog.bValue.text()), 255))
            else:
                newPoly.color = (0,0,0,255)
            self.drawOne(newPoly)
            self.status.addItem("Polígono 3D adicionado com sucesso.")
        else:
            self.status.addItem("Falha ao adicionar polígono 3D.")
        self.update()
    
    def transformaWindow(self):
        if self.objectList.currentRow() == -1:
            self.status.addItem("Erro: nenhum objeto selecionado.")
            return

        if self.displayFile[self.objectList.currentRow()].dimension == 2:
            self.transforma2D()
        else:
            self.transforma3D()
    
    def transforma2D(self):
        print("TRANSFORMA 2D")
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
                
    def transforma3D(self):
        print("TRANSFORMA 3D")
        transformaDialog = UiTransforma3D()
        if transformaDialog.exec_():
            if transformaDialog.transX.text() or transformaDialog.transY.text() or transformaDialog.transZ.text():
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
                    
                if transformaDialog.transZ.text():
                    Dz = int(transformaDialog.transZ.text())
                else:
                    Dz = 0

                self.translacao3D(obj, Dx, Dy, Dz)
                self.status.addItem(obj.name + " transladado com sucesso.")
                self.drawAll()

            if transformaDialog.escX.text() or transformaDialog.escY.text() or transformaDialog.escZ.text():
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
                    
                if transformaDialog.escZ.text():
                    Sz = int(transformaDialog.escZ.text())
                else:
                    Sz = 1

                self.escalonamento3D(obj, Sx, Sy, Sz)
                self.status.addItem(obj.name + " escalonado com sucesso.")
                self.drawAll()

            if transformaDialog.rotX.text() or transformaDialog.rotY.text() or transformaDialog.rotZ.text():
                obj = self.displayFile[self.objectList.currentRow()]
                print(obj.name)
                
                if transformaDialog.rotX.text():
                    Rx = int(transformaDialog.rotX.text())
                else:
                    Rx = 0
                    
                if transformaDialog.rotY.text():
                    Ry = int(transformaDialog.rotY.text())
                else:
                    Ry = 0
                    
                if transformaDialog.rotZ.text():
                    Rz = int(transformaDialog.rotZ.text())
                else:
                    Rz = 0
                    
                self.rotacao3D(obj, Rx, Ry, Rz, 
                             transformaDialog.rotOrigem.isChecked(), 
                             transformaDialog.rotObject.isChecked(),
                             transformaDialog.rotPoint.isChecked(),
                             transformaDialog.rotPointX.text(),
                             transformaDialog.rotPointY.text(),
                             transformaDialog.rotPointZ.text())
                self.status.addItem(obj.name + " rotacionado com sucesso.")
                self.drawAll()
                self.status.addItem(obj.name + " transformado com sucesso.")

    def rodaWindow(self):
        rotDialog = UiRotWin()
        if rotDialog.exec_():
            if rotDialog.rotX.text() or rotDialog.rotY.text() or rotDialog.rotZ.text():
                if (rotDialog.rotX.text()):
                    angX = int(rotDialog.rotX.text())
                else:
                    angX = 0
                self.windowAngle[0] -= angX
                
                if (rotDialog.rotY.text()):
                    angY = int(rotDialog.rotY.text())
                else:
                    angY = 0
                self.windowAngle[1] -= angY
                
                if (rotDialog.rotZ.text()):
                    angZ = int(rotDialog.rotZ.text())
                else:
                    angZ = 0
                self.windowAngle[2] -= angZ
                
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

        if obj.type == "Point3D":
            return (obj.x, obj.y, obj.z)
        
        if obj.type == "Polygon3D":
            x, y, z = 0, 0, 0
            for i in obj.points:
                x += i.x
                y += i.y
                z += i.z
            x, y, z = x//len(obj.points), y//len(obj.points), z//len(obj.points)
            return(x, y, z)

    def find_window_center(self):
        x = (self.cgWindow.xMin + self.cgWindow.xMax)/2
        y = (self.cgWindow.yMin + self.cgWindow.yMax)/2
        return (x,y)

    def makePPCmatrix(self):
        width = self.cgWindow.xMax - self.cgWindow.xMin
        height = self.cgWindow.yMax - self.cgWindow.yMin
        center = self.find_window_center()
        
        #2D
        matTrans =  [   [1, 0, 0],
                        [0, 1, 0],
                        [-center[0], -center[1], 1]
                    ]

        angZ = np.deg2rad(self.windowAngle[2])
        angX = np.deg2rad(self.windowAngle[0])
        angY = np.deg2rad(self.windowAngle[1])

        matRot =    [   [np.cos(angZ), -np.sin(angZ), 0],
                        [np.sin(angZ), np.cos(angZ), 0],
                        [0, 0, 1]
                    ]
        
        matScale =  [   [2/width,   0,          0],
                        [0,         2/height,   1],
                        [0,         0,          1]

                    ]
        
        matPPC = np.dot(np.dot(matTrans, matRot), matScale)
        self.ppcMatrix = matPPC
        
        #3D
        matTrans3D =  [   [1, 0, 0, 0],
                        [0, 1, 0, 0],
                        [0, 0, 1, 0],
                        [-center[0], -center[1], 1, 1]
                    ]

        angZ = np.deg2rad(self.windowAngle[2])
        angX = np.deg2rad(self.windowAngle[0])
        angY = np.deg2rad(self.windowAngle[1])

        Rx = [  [1, 0, 0, 0],
                    [0, np.cos(angX), np.sin(angX), 0],
                    [0, -np.sin(angX), np.cos(angX), 0],
                    [0, 0, 0, 1],
                ]
        Ry = [  [np.cos(angY), 0, -np.sin(angY), 0],
                [0, 1, 0, 0],
                [np.sin(angY), 0, np.cos(angY), 0],
                [0, 0, 0, 1],
            ]
        Rz = [  [np.cos(angZ), np.sin(angZ), 0, 0],
                [-np.sin(angZ), np.cos(angZ), 0, 0],
                [0, 0, 1, 0],
                [0, 0, 0, 1],
            ]
        
        matRot3D = np.dot(np.dot(Rx, Ry), Rz)
        
        matScale3D =  [   [2/width,   0,          0, 0],
                        [0,         2/height,   0, 0],
                        [0,         0,          1, 0],
                        [0 , 0, 0 , 1]
                    ]
        
        matPPC3D = np.dot(np.dot(matTrans3D, matRot3D), matScale3D)
        self.ppcMatrix3D = matPPC3D

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
        elif obj.type == "Polygon" or obj.type == "Curve":
            print(obj.points)
            for p in obj.points:
                P = (p.x, p.y, 1)
                (X,Y,W) = np.matmul(P, self.ppcMatrix)
                p.cn_x = X
                p.cn_y = Y
        elif obj.type == "Point3D": 
            if self.projPersp.isChecked():
                nx = obj.x/(obj.z/self.perspd)
                ny = obj.y/(obj.z/self.perspd)
                P = (nx, ny, obj.z, 1)
            else:
                P = (obj.x, obj.y, obj.z, 1)
            
            (X,Y,Z,_) = np.dot(P, self.ppcMatrix3D)
            obj.cn_x = X
            obj.cn_y = Y
            obj.cn_z = Z
        elif obj.type == "Polygon3D":
            for p in obj.points:
                if self.projPersp.isChecked():
                    nx = p.x/(p.z/self.perspd)
                    ny = p.y/(p.z/self.perspd)
                    P = (nx, ny, p.z, 1)
                else:
                    P = (p.x, p.y, p.z, 1)
                 
                print("ORIG E PERSP")
                print((p.x, p.y, p.z, 1))
                print(P)
                
                (X,Y,Z, W) = np.matmul(P, self.ppcMatrix3D)
                p.cn_x = X
                p.cn_y = Y
                p.cn_z = Z

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
                
    def translacao3D(self, obj, Dx, Dy, Dz):
        if obj.type == "Point3D":
            P = [obj.x, obj.y, obj.z, 1]
            T = [   [1, 0, 0, 0],
                    [0, 1, 0, 0],
                    [0, 0, 1, 0],
                    [Dx, Dy, Dz, 1]
                ]
            (X,Y,Z, _) = np.matmul(P, T)
            obj.x = X
            obj.y = Y
            obj.z = Z

        elif obj.type == "Polygon3D":
            T = [   [1, 0, 0, 0],
                    [0, 1, 0, 0],
                    [0, 0, 1, 0],
                    [Dx, Dy, Dz, 1]
                ]
            for p in obj.points:
                P = (p.x, p.y, p.z, 1)
                (X,Y,Z, _) = np.matmul(P, T)
                p.x = X
                p.y = Y
                p.z = Z

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
        
    def escalonamento3D(self, obj, Sx, Sy, Sz):
        centroInicial = self.find_center(obj)
        if obj.type == "Point3D":
            P = [obj.x, obj.y, obj.z, 1]
            T = [   [Sx, 0, 0, 0],
                    [0, Sy, 0, 0],
                    [0, 0, Sz, 0],
                    [0, 0, 0, 1]
                ]
            (X,Y,Z,_) = np.matmul(P, T)
            obj.x = X
            obj.y = Y
            obj.z = Z
        
        elif obj.type == "Polygon3D":
            centroInicial = self.find_center(obj)

            T = [   [Sx, 0, 0, 0],
                    [0, Sy, 0, 0],
                    [0, 0, Sz, 0],
                    [0, 0, 0, 1]
                ]
            for p in obj.points:
                P = (p.x, p.y, p.z, 1)
                (X,Y,Z,_) = np.matmul(P, T)
                p.x = X
                p.y = Y
                p.z = Z

        centroFinal = self.find_center(obj)
        print(centroFinal)
        dist = (centroInicial[0] - centroFinal[0], centroInicial[1] - centroFinal[1], centroInicial[2] - centroFinal[2])
        #print(centroInicial)
        #print(centroFinal)
        #print(dist)
        self.translacao3D(obj, dist[0], dist[1], dist[2])

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
            
    def rotacao3D(self, obj, rotX, rotY, rotZ, toOrigin, toObject, toPoint, pX, pY, pZ):
        rotX = np.deg2rad(rotX)
        rotY = np.deg2rad(rotY)
        rotZ = np.deg2rad(rotZ)
        centroInicial = self.find_center(obj)
        if toObject:
            self.translacao3D(obj, -centroInicial[0], -centroInicial[1], -centroInicial[2])
        elif toPoint:
            #Nao sei se ta certo
            if not pX or not pY or not pZ:
                self.status.addItem("Erro: ponto de rotação não especificado.")
                return
            self.translacao(obj, -int(pX), -int(pY), -int(pZ))

        if obj.type == "Point":
            P = [obj.x, obj.y, obj.z, 1]
            Tx = [  [1, 0, 0, 0],
                    [0, np.cos(rotX), np.sin(rotX), 0],
                    [0, -np.sin(rotX), np.cos(rotX), 0],
                    [0, 0, 0, 1],
                ]
            Ty = [  [np.cos(rotY), 0, -np.sin(rotY), 0],
                    [0, 1, 0, 0],
                    [np.sin(rotY), 0, np.cos(rotY), 0],
                    [0, 0, 0, 1],
                ]
            Tz = [  [np.cos(rotZ), np.sin(rotZ), 0, 0],
                    [-np.sin(rotZ), np.cos(rotZ), 0, 0],
                    [0, 0, 1, 0],
                    [0, 0, 0, 1],
                ]
            R = np.matmul(P, Tx)
            R = np.matmul(R, Ty)
            (X, Y, Z, _) = np.matmul(R, Tz)
            obj.x = X
            obj.y = Y
            obj.z = Z

        elif obj.type == "Polygon3D":
            Tx = [  [1, 0, 0, 0],
                    [0, np.cos(rotX), np.sin(rotX), 0],
                    [0, -np.sin(rotX), np.cos(rotX), 0],
                    [0, 0, 0, 1],
                ]
            Ty = [  [np.cos(rotY), 0, -np.sin(rotY), 0],
                    [0, 1, 0, 0],
                    [np.sin(rotY), 0, np.cos(rotY), 0],
                    [0, 0, 0, 1],
                ]
            Tz = [  [np.cos(rotZ), np.sin(rotZ), 0, 0],
                    [-np.sin(rotZ), np.cos(rotZ), 0, 0],
                    [0, 0, 1, 0],
                    [0, 0, 0, 1],
                ]
            for p in obj.points:
                P = (p.x, p.y, p.z, 1)
                R = np.matmul(P, Tx)
                R = np.matmul(R, Ty)
                (X, Y, Z, _) = np.matmul(R, Tz)
                p.x = X
                p.y = Y 
                p.z = Z

        if toObject:
            self.translacao3D(obj, centroInicial[0], centroInicial[1], centroInicial[2])
        elif toPoint:
            #Nao sei se ta certo
            self.translacao3D(obj, int(pX), int(pY), int(pZ))

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
        ang = np.deg2rad(self.windowAngle[2])
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
        ang = np.deg2rad(self.windowAngle[2])
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
        ang = np.deg2rad(self.windowAngle[2])
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
        ang = np.deg2rad(self.windowAngle[2])
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

        self.windowAngle = [0, 0, 0]

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
        
    def perspChange(self):
        self.perspd = self.perspSlider.value()
        self.drawAll()
        
    def cuboteste(self):
        ps = []
        ps.append(Point3D(100, 100, 100))
        ps.append(Point3D(200, 100, 100))
        ps.append(Point3D(200, 200, 100))
        ps.append(Point3D(100, 200, 100))
        
        ps.append(Point3D(100, 100, 200))
        ps.append(Point3D(200, 100, 200))
        ps.append(Point3D(200, 200, 200))
        ps.append(Point3D(100, 200, 200))
        
        edges = []
        edges.append((0, 1))
        edges.append((1, 2))
        edges.append((2, 3))
        edges.append((3, 0))
        
        edges.append((4, 5))
        edges.append((5, 6))
        edges.append((6, 7))
        edges.append((7, 4))
        
        edges.append((0, 4))
        edges.append((1, 5))
        edges.append((2, 6))
        edges.append((3, 7))
        
        cuboteste = Object3D(ps, edges, "CUBOTESTE")
        self.displayFile.append(cuboteste)
        self.objectList.addItem(cuboteste.name)
        self.status.addItem("CUBOTESTE adicionado com sucesso.")
        self.drawOne(cuboteste)
        self.update()
    #Fazer um método pra dar self.painter.end() no término do programa
