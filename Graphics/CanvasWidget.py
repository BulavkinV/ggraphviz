import random
import copy

from PyQt5 import QtWidgets, QtGui, QtCore

from Graphics.CanvasHyperEdge import CanvasHyperEdge
from Graphics.CanvasVertex import CanvasVertex

from Hypergraph import HyperGraph

class HyperGraphCanvas(QtWidgets.QGraphicsScene, HyperGraph):
    
    def __init__(self, **kwargs):
        QtWidgets.QGraphicsScene.__init__(self)

        HyperGraph.__init__(
            self,
            edges = [CanvasHyperEdge(x) for x in kwargs.pop('edges', [])],
            vertices = {CanvasVertex(x) for x in kwargs.pop('vertices', set())}
        )

    
    def drawVertices(self, vertices:set()):
        for vertex in vertices:
            self.drawVertex(vertex)

    def drawVertex(self, vertex:CanvasVertex):
        if vertex in filter(lambda item: isinstance(item, CanvasVertex), self.items()):
            return
        while True:
            vertex.setX(random.randint(0,100))
            vertex.setY(random.randint(0,100))
            if not self.collidingItems(vertex):
                break

        self.addItem(
            vertex
        )

    def drawEdges(self, edges:list):
        for edge in edges:
            self.drawEdge(edge)

    def drawEdge(self, edge: CanvasHyperEdge):
        self.addItem(edge)

    def addVertex(self, vertex:CanvasVertex):
        vertex = CanvasVertex(vertex)
        super().addVertex(vertex)
        # self.drawVertex(vertex)

    def addVertices(self, vertices:set):
        vertices = {CanvasVertex(x) for x in vertices}
        super().addVertices(vertices)
        # self.drawVertices(vertices)

    def addEdge(self, edge:CanvasHyperEdge):
        edge = CanvasHyperEdge(edge=edge)
        super().addEdge(edge)
        self.drawEdge(edge)

    def addEdges(self, edges):
        edges = [CanvasHyperEdge(edge=edge) for edge in edges]
        super().addEdges(edges)
        self.drawEdges(edges)

    def update(self, rect=QtCore.QRectF()):
        print('update')
        super().update(rect)

    # def render(self, *args, **kwargs):
    #     # print("render")
    #     # self.drawVertices()
    #     super().render(*args, **kwargs)
        

class CanvasWidget(QtWidgets.QGraphicsView):
    
    def __init__(self, scene:HyperGraphCanvas):
        super().__init__(scene)

        # self.setFrameStyle(QtWidgets.QFrame.Box)

