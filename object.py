from dataclasses import dataclass

@dataclass
class Point:
    x: int
    y: int

    def draw(self, painter):
        painter.drawPoint(self.x, self.y)

@dataclass
class Line:
    p1: Point
    p2: Point

    def draw(self, painter):
        painter.drawLine(self.p1.x, self.p1.y, self.p2.x, self.p2.y)

@dataclass
class Wireframe:
    lines: list[Line]

    def draw(self, painter):
        for line in self.lines:
            line.draw(painter)
