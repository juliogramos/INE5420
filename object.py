from dataclasses import dataclass

@dataclass
class Point:
    x: int
    y: int

    def draw(self, painter):
        painter.drawPoint(self.x, self.y)
        print("paintou")

@dataclass
class Line:
    p1: Point
    p2: Point

    def draw(self, painter):
        painter.drawLine(self.p1.x, self.p1.y, self.p2.x, self.p2.y)

@dataclass
class Wireframe:
    points: list[Point]

    def draw(self, painter):
        for i in range(len(self.points)):
            if i == 0:
                Line(self.points[0], self.points[i+1]).draw(painter)
            elif i == (len(self.points)):
                Line(self.points[i], self.points[0]).draw(painter)
            else:
                Line(self.points[i], self.points[i+1]).draw(painter)
