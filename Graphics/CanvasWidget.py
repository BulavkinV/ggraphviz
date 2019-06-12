from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QGraphicsView

from Graphics.CanvasHyperGraph import CanvasHyperGraph

class CanvasWidget(QGraphicsView):
    
    def __init__(self, scene:CanvasHyperGraph):
        super().__init__(scene)
        self.setMouseTracking(True)

    def loadHypergraphSlot(self):
        filename = QFileDialog.getOpenFileName(self, caption="Открыть файл гиперграфа",
                                               filter="Json files (*.json);; All Files (*)")
        if not filename[0]:
            return

        # TODO preprocess input file
        new_hg = CanvasHyperGraph()
        new_hg.loadJson(filename)
        self.setScene(new_hg)
        # with open(filename[0], "r") as resultfile:
        #     self.graph.plotResult(resultfile.read())

    def saveHypergraphSlot(self):
        print("Let's try to save something!")

    def resetSceneSlot(self):
        self.setScene(CanvasHyperGraph())

    def addVertexForCurrentSceneSlot(self):
        self.scene().addVertexSlot()

    def removeVertexForCurrentSceneSlot(self):
        self.scene().removeVertexSlot()

    def addEdgeForCurrentSceneSlot(self):
        self.scene().addEdgeSlot()

    def removeEdgeForCurrentSceneSlot(self):
        self.scene().removeEdgeSlot()