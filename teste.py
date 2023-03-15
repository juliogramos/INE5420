import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import Qt

class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('testeui.ui', self)

        canvas = QtGui.QPixmap(400, 300)
        canvas.fill(Qt.white)
        self.mainLabel.setPixmap(canvas)
        self.draw_something()

    def draw_something(self):
        painter = QtGui.QPainter(self.mainLabel.pixmap())
        painter.drawLine(10, 10, 300, 200)
        painter.end()

    def drawPoints(self, qp):
        qp.setBrush(QBrush(Qt.red, Qt.SolidPattern))
        size = self.size()

        if size.height() <= 1 or size.height() <= 1:
            return

        #for i in range(1000):
            #x = random.randint(1, size.width() - 1)
            #y = random.randint(1, size.height() - 1)
        qp.drawPoint(500, 500)


app = QtWidgets.QApplication(sys.argv)
window = Ui()
window.show()
app.exec_()
