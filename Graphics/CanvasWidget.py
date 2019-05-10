from PyQt5 import QtWidgets

from Graphics.CanvasHyperGraph import HyperGraphCanvas

class CanvasWidget(QtWidgets.QGraphicsView):
    
    def __init__(self, scene:HyperGraphCanvas):
        super().__init__(scene)

        # self.setFrameStyle(QtWidgets.QFrame.Box)

