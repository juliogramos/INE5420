import pathlib
from PyQt5 import QtGui, QtCore

from object import Point, Line, Wireframe

class DescritorOBJ:
    def __init__(self):
        pass

    def parseObj(self, file_path, parse_dict):
        with open(file_path) as file:
            sequence = []
            for line in file.readlines():
                split = line.split()
                try:
                    type = split[0]
                    args = split[1:]
                    sequence.append((type, args))
                except IndexError:
                    # blank line
                    pass
    
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
                currentMtl = e[0]
            elif e[0] == "Kd":
                r, g, b = e[1]
                r = round(float(r) * 255)
                g = round(float(g) * 255)
                b = round(float(b) * 255)
                cores[currentMtl] = (r,g,b)
        return cores

        


    def processObjects(self, sequence):
        """ commands = {
                "v": [],
                "o": [],
                "usemtl": [],
                "mtlib": [],
                "p": [],
                "f": [],
                "l": []
            } """
        
        verts = []
        prev = ""
        vertsEnded = False
        objects = []

        for e in sequence:
            if e[0] == "v":
                (x, y, _) = e[1]
                newVert = Point(x, y)
                verts.append(newVert)
            elif e[0] == "o":
                pass
        prev = e[0]

        #Tratar todos os comandos
        #Talvez mudar os obj para salvar a cor
        #Arrumar um jeito de retornar a cor deles

    """def vertice_handler(self, args):
        x = float(args[0])
        y = float(args[1])
        # z = float(args[2])
        vertex = (x, y)
        self.vertices.append(vertex)

    def mtllib_handler(self, args):
        file = args[0]
        file_path = str(pathlib.Path().absolute() / "obj" / file)
        self.parse_file(file_path, self.mtl_parser)

    def usemtl_handler(self, args):
        mtl = args[0]
        self.mtl = self.mtl_dict[mtl]

    def object_name_handler(self, args):
        name = args[0]
        self.obj_parsing = name

    def object_build_handler(self, args):
        points = []
        for vertex in args:
            if vertex[0] == "-":
                index = int(vertex)
                points.append(self.vertices[index])
            else:
                index = int(vertex) - 1
                points.append(self.vertices[index])
        if not self.mtl:
            self.mtl = QtCore.Qt.black
        wireframe = Wireframe(
            points,
            self.wireframe_index,
            self.mtl,
            self.normalization_values,
            self.window_transformations,
        )
        wireframe.name = self.obj_parsing
        print(wireframe.name)
        self.wireframes.append(wireframe)
        self.wireframe_index += 1
        self.mtl = None
        self.obj_parsing = ""

    obj_parser = {
        "v": vertice_handler,
        "mtllib": mtllib_handler,
        "usemtl": usemtl_handler,
        "o": object_name_handler,
        "w": object_build_handler,
        "p": object_build_handler,
        "l": object_build_handler,
        "f": object_build_handler,
    }

    def newmtl_handler(self, args):
        self.mtl_parsing = args[0]

    def Kd_handler(self, args):
        r = int(float(args[0]) * 255)
        g = int(float(args[1]) * 255)
        b = int(float(args[2]) * 255)
        color = QtGui.QColor(r, g, b)
        self.mtl_dict[self.mtl_parsing] = color
        self.mtl_parsing = ""

    mtl_parser = {"newmtl": newmtl_handler, "Kd": Kd_handler}

    def load(self, file_path):
        self.parse_file(file_path, self.obj_parser)

    def parse_file(self, file_path, parse_dict):
        with open(file_path) as file:
            for line in file.readlines():
                split = line.split()
                try:
                    statement = split[0]
                    args = split[1:]
                    parse_dict[statement](self, args)
                except IndexError:
                    # blank line
                    pass """

