import random
import copy

from PyQt5 import QtWidgets, QtGui, QtCore 

from Graphics.CanvasHyperEdge import CanvasHyperEdge
from Graphics.CanvasVertex import CanvasVertex

from Hypergraph import HyperGraph

class CanvasHyperGraph(QtWidgets.QGraphicsScene, HyperGraph):
    
    def __init__(self, hypergraph:HyperGraph=None, **kwargs):
        QtWidgets.QGraphicsScene.__init__(self)

        if hypergraph:
            HyperGraph.__init__(self, other=hypergraph)
        else:
            HyperGraph.__init__(
                self,
                edges = kwargs.pop('edges', []),
                vertices = kwargs.pop('vertices', set())
            )

        self.setSceneRect(-200., -200., 400., 400.)

        # self.addItem(CanvasVertex("new_point"))
        # minus_verttex = CanvasVertex("50 point")
        # minus_verttex.setPos(0., 50.)
        # self.addItem(minus_verttex)

        self.vertices = {CanvasVertex(other=x) for x in self.vertices}
        self.edges = [CanvasHyperEdge(other=x) for x in self.edges]

        for vertex in self.vertices:
            self.addItem(vertex)
            
            # randomising vertices positions
            vertex.setPos(QtCore.QPointF(random.uniform(-200., 200.), random.uniform(-200., 200.)))

        # self.edges = [CanvasHyperEdge(x, self.vertices) for x in hg.getEdges()]
        
        # checking crossing variants
        self.crossing_matrix = [ [False]*len(self.edges) for _ in range(len(self.edges)) ]
        for i, edge in enumerate(self.edges[:-1]):
            for j, other in enumerate(self.edges[i+1:], i+1):
                self.crossing_matrix[i][j] = edge.getCrossingVariant(other)

        # matrix reflection
        for i in range(len(self.crossing_matrix)):
            for j in range(i):
                self.crossing_matrix[i][j] = self.crossing_matrix[j][i]

        # # reflection test
        # for i in range(len(self.crossing_matrix)):
        #     for j in range(len(self.crossing_matrix)):
        #         assert self.crossing_matrix[i][j] == self.crossing_matrix[j][i], "Bad reflection"

        for edge in self.edges:
            if edge.isHyperedge():
                edge.grahamConvex(self.vertices)
                edge.draw()
                self.addItem(edge)
                support_convex = edge.getSupportConvex()
                
                # for i, item in enumerate(support_convex):
                #     vertex = CanvasVertex(id=str(i)+ '!')
                #     vertex.setPos(item)
                #     self.addItem(vertex)
        

    
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

    def addVertex(self, vertex:CanvasVertex, edge:CanvasHyperEdge=None):
        super().addVertex(vertex, edge)
        self.addItem(vertex)

    def addVertices(self, vertices:set, edge:CanvasHyperEdge=None):
        for vertex in vertices:
            self.addVertex(vertex, edge)

    def addEdge(self, edge:CanvasHyperEdge):
        edge = CanvasHyperEdge(edge=edge)
        super().addEdge(edge)
        # self.drawEdge(edge)

    def addEdges(self, edges):
        edges = [CanvasHyperEdge(edge=edge) for edge in edges]
        super().addEdges(edges)
        # self.drawEdges(edges)

    def update(self, rect=QtCore.QRectF()):
        print('update')
        super().update(rect)

    # def render(self, *args, **kwargs):
    #     # print("render")
    #     # self.drawVertices()
    #     super().render(*args, **kwargs)