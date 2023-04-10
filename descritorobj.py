import pathlib
from PyQt5 import QtGui, QtCore
import PyQt5
from PyQt5.QtCore import Qt
from dataclasses import dataclass

from object import Point, Line, Wireframe

@dataclass
class PreObject:
    name: str = ""
    color: tuple = (0,0,0)

class DescritorOBJ:
    def __init__(self):
        pass

    def load(self, file_path):
        sequence = self.parseObj(file_path)
        print(sequence)
        return self.processObjects(sequence)

    def parseObj(self, file_path):
        path = str(pathlib.Path().absolute() / "obj" / file_path)
        sequence = []
        with open(path) as file:
            for line in file.readlines():
                split = line.split()
                try:
                    type = split[0]
                    args = split[1:]
                    sequence.append((type, args))
                except IndexError:
                    # blank line
                    pass
        return sequence
    
    def parseMtl(self, file_path):
        sequence = []
        with open(file_path) as file:
            for line in file.readlines():
                split = line.split()
                try:
                    type = split[0]
                    args = split[1:]
                    sequence.append((type, args))
                except IndexError:
                    # blank line
                    pass
        
        cores = {}
        currentMtl = ""
        for e in sequence:
            if e[0] == "newmtl":
                cores[e[1][0]] = None
                currentMtl = e[1][0]
            elif e[0] == "Kd":
                r, g, b = e[1]
                r = round(float(r) * 255)
                g = round(float(g) * 255)
                b = round(float(b) * 255)
                cores[currentMtl] = (r,g,b)
        return cores

        


    def processObjects(self, sequence):
        commands = {
                "v": [], # ok
                "o": [], # ok
                "usemtl": [], # ok
                "mtlib": [],   
                "p": [], #ok
                "f": [], #ok
                "l": [] #ok
            }
        verts = []
        objIndex = -1
        preobjects = []
        cores = None
        objects = []
        for e in sequence:
            if e[0] == "v":
                (x, y, _) = e[1]
                newVert = Point(int(float(x)), int(float(y)))
                verts.append(newVert)
            
            elif e[0] == "o":
                objIndex += 1
                newObj = PreObject(e[1])
                newObj.name = newObj.name[0]
                preobjects.append(newObj)
                print(newObj.name)

            elif e[0] == "usemtl":
               cor = cores[e[1][0]]
               preobjects[objIndex].color = cor

            elif e[0] == "mtlib":
                file = e[1][0]
                file_path = str(pathlib.Path().absolute() / "obj" / file)
                cores = self.parseMtl(file_path)
                print(cores)

            elif e[0] == "p":
                index = int(e[1][0])
                newPoint = verts[index-1]
                newPoint.name = preobjects[objIndex].name
                newPoint.color = preobjects[objIndex].color
                objects.append(newPoint)

            elif e[0] == "l":
                points = e[1]
                p1 = verts[int(points[0])-1]
                p2 = verts[int(points[1])-1]
                newLine = Line(p1, p2, preobjects[objIndex].name, preobjects[objIndex].color)
                objects.append(newLine)

            elif e[0] == "f":
                print(e[1])
                points = e[1]
                pointList = []
                for p in points:
                    realPoint = verts[int(p)-1]
                    pointList.append(realPoint)
                newPoly = Wireframe(pointList, preobjects[objIndex].name, preobjects[objIndex].color)
                objects.append(newPoly)

            else:
                print("COMANDO NAO RECONHECIDO")
        return objects

