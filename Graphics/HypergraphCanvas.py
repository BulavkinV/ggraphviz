import random
import copy

from PyQt5 import QtWidgets, QtGui, QtCore

from Graphics.CanvasHyperEdge import CanvasHyperEdge
from Graphics.CanvasVertex import CanvasVertex

from Hypergraph import HyperGraph


class HyperGraphCanvas(QtWidgets.QGraphicsScene):
    
    def __init__(self, hg:HyperGraph):
        self.hypergraph = hg

        super().__init__()

        self.vertices = [CanvasVertex(x) for x in hg.getVertices()]
        for vertex in self.vertices:
            self.addItem(vertex)
            
            # randomising vertices positions
            vertex.setPos(QtCore.QPointF(random.uniform(-100., 100.), random.uniform(-100., 100.)))

        self.edges = [CanvasHyperEdge(x, self.vertices) for x in hg.getEdges()]
        
        # checking crossing variants
        self.crossing_matrix = [ [False]*len(self.edges) for _ in range(len(self.edges)) ]
        for i, edge in enumerate(self.edges[:-1]):
            for j, other in enumerate(self.edges[i+1:], i+1):
                self.crossing_matrix[i][j] = edge.hyperedge.getCrossingVariant(other.hyperedge)

        # matrix reflection
        for i in range(len(self.crossing_matrix)):
            for j in range(i):
                self.crossing_matrix[i][j] = self.crossing_matrix[j][i]

        # reflection test
        # for i in range(len(self.crossing_matrix)):
        #     for j in range(len(self.crossing_matrix)):
        #         assert self.crossing_matrix[i][j] == self.crossing_matrix[j][i], "Bad reflection"

        for edge in self.edges:
            if edge.hyperedge.isHyperedge():
                edge.grahamConvex()


        

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