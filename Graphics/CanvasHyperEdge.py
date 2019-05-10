from PyQt5 import QtWidgets, QtGui, QtCore

from Vertex import Vertex
from HyperEdge import HyperEdge

from Graphics.CanvasVertex import CanvasVertex

class CanvasHyperEdge(QtWidgets.QGraphicsPathItem):
    
    def __init__(self, he:HyperEdge, vertices:set):
        super().__init__()

        self.hyperedge = he
        self.convex_vertices = { x for x in vertices if x in self.hyperedge.getVertices() }

    def convexVertexBelongsToEdge(self, vertex:CanvasVertex):
        return vertex in self.convex_vertices

    def vertexBelongsToEdge(self, vertex:Vertex):
        return vertex in self.hyperedge.getVertices()

    def grahamConvex(self) -> list:
        if not self.hyperedge.isHyperedge():
            raise Exception("Convex can be calculated for edges with degree > 2!")
        
        print([point.pos().y for point in self.convex_vertices])

    def getVertices(self) -> set:
        return self.hyperedge.getVertices()

    def __str__(self) -> str:
        return str(self.hyperedge)


        # QtWidgets.QGraphicsPathItem.__init__(self)
        # if 'edge' in kwargs:
        #     edge = kwargs.pop('edge')
        #     HyperEdge.__init__(self, *[CanvasVertex(vertex, self) for vertex in edge.getVertices()])
        # else:
        #     HyperEdge.__init__(self, *[CanvasVertex(vertex, self) for vertex in vertices], **kwargs)

        # self.default_pen = QtGui.QPen()
        # self.setPen(self.default_pen)

        # if self.getDegree() == 2:
        #     vertices = list(self.getVertices())
        #     vertices[1].setPos(50., 0.)                
        #     path = QtGui.QPainterPath(vertices[0].pos())
        #     path.lineTo(vertices[1].pos())
        #     self.setPath(path)