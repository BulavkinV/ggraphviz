from PyQt5.QtWidgets import QGraphicsView

from Graphics.CanvasHyperEdge import CanvasHyperEdge 

class CanvasWidget(QGraphicsView):
    
    def __init__(self, scene:CanvasHyperEdge):
        super().__init__(scene)
        
        # self.setFrameStyle(QtWidgets.QFrame.Box)

