import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import Qt

from object import Point, Line, Wireframe

class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('testeui.ui', self)

        self.setCanvas()
        self.setPainter()

        self.draw_something()


    def setCanvas(self):
        self.canvas = QtGui.QPixmap(400, 400)
        self.canvas.fill(Qt.white)
        self.mainLabel.setPixmap(self.canvas)

    def setPainter(self):
        self.painter = QtGui.QPainter(self.mainLabel.pixmap())
        self.pen = QtGui.QPen(Qt.red)
        self.pen.setWidth(5)
        self.painter.setPen(self.pen)

    def draw_something(self):
        p1 = Point(50, 200)
        p2 = Point (300, 300)
        l1 = Line(Point(5,5), Point(105, 105))
        l2 = Line(Point(200,400), Point(200, 0))
        objList = [p1, p2, l1, l2]

        for obj in objList:
            obj.draw(self.painter)

    #Fazer um método pra dar self.painter.end() no término do programa