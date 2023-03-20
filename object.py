from dataclasses import dataclass

@dataclass
class Point:
    x: int
    y: int
    name: str
    type: str = "Point"

    def draw(self, painter):
        painter.drawPoint(self.x, self.y)
        print("paintou")

@dataclass
class Line:
    p1: Point
    p2: Point
    name: str
    type: str = "Line"

    def draw(self, painter):
        painter.drawLine(self.p1.x, self.p1.y, self.p2.x, self.p2.y)

@dataclass
class Wireframe:
    points: list[Point]
    name: str
    type: str = "Polygon"

    def draw(self, painter):
        for i in range(1, len(self.points)):
            Line(self.points[i-1], self.points[i], "").draw(painter)
        Line(self.points[-1], self.points[0], "").draw(painter)