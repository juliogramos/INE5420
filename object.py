from dataclasses import dataclass

@dataclass
class Point:
    x: int
    y: int
    name: str = ""
    cn_x: int = 0
    cn_y: int = 0
    type: str = "Point"

@dataclass
class Line:
    p1: Point
    p2: Point
    name: str = ""
    type: str = "Line"

@dataclass
class Wireframe:
    points: list[Point]
    name: str = ""
    type: str = "Polygon"