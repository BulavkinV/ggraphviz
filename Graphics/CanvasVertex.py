from PyQt5 import QtWidgets, QtGui, QtCore

from Vertex import Vertex

class CanvasVertex(QtWidgets.QGraphicsItem):
    """
    """

    # TODO 

    def __init__(self, vertex:Vertex):
        super().__init__()

        self.vertex = vertex

        self.vertex_width = 10.
        self.vertex_height = 10.
        self.vertex_text_gap = 0.

        self.vertex_ellipse_rect = QtCore.QRectF(
            -self.vertex_width/2., -self.vertex_height/2,
            self.vertex_width, self.vertex_height
        )
        self.ellipse_default_brush = QtGui.QBrush(QtCore.Qt.black)
        self.ellipse = QtWidgets.QGraphicsEllipseItem(self.vertex_ellipse_rect, self)
        self.ellipse.setBrush(self.ellipse_default_brush)

        self.text = QtWidgets.QGraphicsSimpleTextItem(self.vertex.getId(), self)
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

    def boundingRect(self):
        return self.childrenBoundingRect()

    # def paint(self, painter, option, widget) -> None:
    #     """
    #         TODO type annotations
    #     """

    #     self.ellipse.paint(painter, option, widget)
    #     self.text.paint(painter, option, widget)




        
        # if 'width' in kwargs and 'height' in kwargs:
        #     pass
        # elif 'rect' in kwargs:
        #     pass


        