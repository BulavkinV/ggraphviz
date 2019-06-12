from __future__ import annotations
from math import atan2, sqrt, atan

from PyQt5 import QtWidgets, QtGui, QtCore

from Vertex import Vertex

class CanvasVertex(Vertex, QtWidgets.QGraphicsItem):
    """
    """

    # TODO 
    def __init__(self, id:str=None, other:CanvasVertex=None):
        
        if other:
            self._copy_constructor(other)
        else:
            self.id = id
            QtWidgets.QGraphicsItem.__init__(self)
        
        self.placed = False

        self.vertex_width = 10.
        self.vertex_height = 10.
        self.vertex_text_gap = 3.

        self.vertex_ellipse_rect = QtCore.QRectF(
            -self.vertex_width/2., -self.vertex_height/2,
            self.vertex_width, self.vertex_height
        ) 
        self.ellipse_default_brush = QtGui.QBrush(QtCore.Qt.black)
        self.ellipse_selected_brush = QtGui.QBrush(QtCore.Qt.red)
        self.ellipse = QtWidgets.QGraphicsEllipseItem(self.vertex_ellipse_rect, self)
        self.ellipse.setBrush(self.ellipse_default_brush)

        self.text = QtWidgets.QGraphicsTextItem(self.getId(), self)
        # self.text.setTextInteractionFlags(QtCore.Qt.TextEditable)
        # self.text.document().contentsChanged.connect(self.changeIdFromText)
        self.text.setPos(
            self.ellipse.pos() + 
            QtCore.QPointF(
                - self.text.boundingRect().width() / 2. , 
                - self.text.boundingRect().height() - self.vertex_height/2. - self.vertex_text_gap
            )
        )
        
        # TODO debug
        # self.x_axis = QtWidgets.QGraphicsLineItem(-100., 0., 100., 0., self)
        # self.y_axis = QtWidgets.QGraphicsLineItem(0., -100., 0., 100., self)
        # QtWidgets.QGraphicsRectItem(self.childrenBoundingRect(), self)

    def _copy_constructor(self, other:CanvasVertex):
        Vertex.__init__(self, other=other)
        QtWidgets.QGraphicsItem.__init__(self)
        if hasattr(other, 'setPos'):
            self.setPos(other.pos())

    def __eq__(self, other:CanvasVertex) -> bool:
        return Vertex.__eq__(self, other)

    def  __hash__(self):
        return Vertex.__hash__(self)

    def isPlaced(self):
        return self.placed

    def setId(self, new_id:str) -> None:
        Vertex.setId(self, new_id)
        self.text.setPlainText(new_id)

    def setPos(self, *args, **kwargs):
        self.placed = True
        QtWidgets.QGraphicsItem.setPos(self, *args, **kwargs)
        # self.text.setText(self.id + ' ' + str([self.pos().x(), self.pos().y()]))

    def unsetPos(self):
        self.placed = False
        QtWidgets.QGraphicsItem.setPos(self, QtCore.QPointF(0., 0.))

    def changeIdFromText(self) -> None:
        self.id = self.text.toPlainText()

    def getText(self):
        return self.text


    # QT functions
    def boundingRect(self):
        return self.childrenBoundingRect()

    def setSelected(self, selected:bool) -> None:
        QtWidgets.QGraphicsItem.setSelected(self, selected)
        if selected:
            self.ellipse.setBrush(self.ellipse_selected_brush)
        else:
            self.ellipse.setBrush(self.ellipse_default_brush)

        self.ellipse.update()

    # math
    def polar_angle(self, other:CanvasVertex):
        # TODO comparsion of vector compositions must be used
        vertex = other.pos() - self.pos()
        return atan2(vertex.y(), vertex.x())
        # return atan(vertex.y()/vertex.x())

    def vector_product(self, p1:CanvasVertex, p2:CanvasVertex):
        u = p1.pos() - self.pos()
        v = p2.pos() - p1.pos()

        return u.x() * v.y() - u.y() * v.x()

    def distance(self, other:CanvasVertex):
        vertex = other.pos() - self.pos()
        return sqrt(vertex.x()**2. + vertex.y()**2.)

    @staticmethod
    def polar_angle_pos(p1:QtCore.QPointF, p2:QtCore.QPointF):
        vertex = p2 - p1
        return atan2(vertex.y(), vertex.x())

    @staticmethod
    def vector_product_pos(p1:QtCore.QPointF, p2:QtCore.QPointF, p3:QtCore.QPointF):
        u = p2 - p1
        v = p3 - p2

        return u.x() * v.y() - u.y() * v.x()

    @staticmethod
    def distance_pos(p1:QtCore.QPointF, p2:QtCore.QPointF):
        vertex = p2 - p1
        return sqrt(vertex.x()**2. + vertex.y()**2.)





        