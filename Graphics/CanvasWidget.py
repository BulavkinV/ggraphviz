from pathlib import Path

from PyQt5.QtWidgets import QFileDialog, QGraphicsView, QToolBar, QMessageBox
from PyQt5 import QtCore

from Hypergraph import HyperGraph
from Graphics.CanvasHyperGraph import CanvasHyperGraph

class CanvasWidget(QGraphicsView):
    
    def __init__(self, scene:CanvasHyperGraph):
        super().__init__(scene)
        self.setMouseTracking(True)

        self._createContractionToolbar()

    def _createContractionToolbar(self):
        toolbar = QToolBar(parent=self)
        toolbar.setFloatable(True)
        toolbar.setMovable(True)
        toolbar.hide()

        action = toolbar.addAction('next')
        action.triggered.connect(self.next_hg)
        action = toolbar.addAction('previous')
        action.triggered.connect(self.previous_hg)
        action = toolbar.addAction('stop')
        action.triggered.connect(self.stopContractionPlayerSlot)

        self.contraction_toolbar = toolbar

    def loadHypergraphSlot(self):
        filename = QFileDialog.getOpenFileName(self, caption="Открыть файл гиперграфа",
                                               filter="Json files (*.json);; All Files (*)")
        if not filename[0]:
            return

        new_hg = HyperGraph()

        file = open(filename[0], 'r')
        new_hg.loadJson(file)
        file.close()

        new_hg = CanvasHyperGraph(new_hg)

        self.setScene(new_hg)

    def saveHypergraphSlot(self):
        filename = QFileDialog.getSaveFileName(self, caption="Сохранить гиперграф",
                                               filter="Json files (*.json);; All Files (*)")

        if not filename[0]:
            return

        self.scene().saveJson(Path(filename[0]))
        # data = self.field.generateJson()
        # with open(filename[0], 'w') as jsonfile:
        #     jsonfile.write(data)

    # contraction player
    def startContractionPlayerSlot(self):
        self.saved_scene = self.scene()
        start_hg = self.saved_scene

        start_hg = HyperGraph(other=start_hg)
        if not start_hg.isContractable():
            msgBox = QMessageBox(self)
            msgBox.setText("Данный гиперграф не является стягиваемым!")
            msgBox.exec()
        else:
            self.contraction_toolbar.show()
            self.current_hg_index = 0
            self.list_of_graphs = list(start_hg.contraction_sequence)

    def next_hg(self):
        if self.current_hg_index == len(self.list_of_graphs) - 1:
            return

        self.current_hg_index += 1
        hg = CanvasHyperGraph(self.list_of_graphs[self.current_hg_index])
        average_pos = QtCore.QPointF()
        contracted_vertex = None
        for v1 in hg.getVertices():
            if v1 not in self.scene().getVertices():
                contracted_vertex = v1
            for v2 in self.scene().getVertices():
                if v1 == v2:
                    v1.setPos(v2.pos())
        average_pos = {v for v in self.scene().getVertices() if v not in hg.getVertices()}
        average_pos = average_pos.pop().pos() + average_pos.pop().pos()
        contracted_vertex.setPos(average_pos /2.)
        hg.drawEdges()
        self.setScene(hg)

    def previous_hg(self):
        if self.current_hg_index == 0:
            return

        self.current_hg_index -= 1
        hg = CanvasHyperGraph(self.list_of_graphs[self.current_hg_index])
        self.setScene(hg)

    def stopContractionPlayerSlot(self):
        self.contraction_toolbar.hide()

        self.setScene(self.saved_scene)

        del self.current_hg_index
        del self.list_of_graphs


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