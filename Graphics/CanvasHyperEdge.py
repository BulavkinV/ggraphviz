from PyQt5 import QtWidgets, QtGui, QtCore

from Graphics.CanvasVertex import CanvasVertex

from HyperEdge import HyperEdge

class CanvasHyperEdge(HyperEdge, QtWidgets.QGraphicsPathItem):
    
    def __init__(self, *vertices, **kwargs):
        QtWidgets.QGraphicsPathItem.__init__(self)
        if 'edge' in kwargs:
            edge = kwargs.pop('edge')
            HyperEdge.__init__(self, *[CanvasVertex(vertex, self) for vertex in edge.getVertices()])
        else:
            HyperEdge.__init__(self, *[CanvasVertex(vertex, self) for vertex in vertices], **kwargs)

        self.default_pen = QtGui.QPen()
        self.setPen(self.default_pen)

        # if self.getDegree() == 2:
        #     vertices = list(self.getVertices())
        #     vertices[1].setPos(50., 0.)                
        #     path = QtGui.QPainterPath(vertices[0].pos())
        #     path.lineTo(vertices[1].pos())
        #     self.setPath(path)