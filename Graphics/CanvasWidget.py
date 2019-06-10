from PyQt5 import QtGui
from PyQt5.QtWidgets import QGraphicsView

from Graphics.CanvasHyperEdge import CanvasHyperEdge 

class CanvasWidget(QGraphicsView):
    
    def __init__(self, scene:CanvasHyperEdge):
        super().__init__(scene)
        self.setMouseTracking(True)

    # def getScene(self):
    #     return self.scene