from PyQt5.QtWidgets import QGraphicsView

from Graphics.HypergraphCanvas import HyperGraphCanvas

class CanvasWidget(QGraphicsView):
    
    def __init__(self, scene:HyperGraphCanvas):
        super().__init__(scene)

        # self.setFrameStyle(QtWidgets.QFrame.Box)

