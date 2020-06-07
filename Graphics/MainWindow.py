from pathlib import Path

from PyQt5 import QtGui
from PyQt5.QtWidgets import QMainWindow, QDesktopWidget, QToolBar, QStatusBar

from Graphics.CanvasHyperGraph import CanvasHyperGraph
from Graphics.CanvasWidget import CanvasWidget

from Hypergraph import HyperGraph
from Vertex import Vertex
from HyperEdge import HyperEdge

class MainWindow(QMainWindow):
    
    def __init__(self, hg_canvas: CanvasHyperGraph):
        self.minimum_size = (800, 600)

        super().__init__()
        self.setCentralWidget(CanvasWidget(hg_canvas))

        desktop = QDesktopWidget()
        self.setMinimumSize(*self.minimum_size)
        self.move(
            desktop.width() // 2 - self.minimum_size[0] // 2, 
            desktop.height() // 2 - self.minimum_size[1] // 2)
        self.setWindowTitle("Визуализация гиперграфов")
        
        # add menu bar
        self.addToolBar(self.createToolbar())

        status_bar = QStatusBar()
        status_bar.showMessage("Готово")
        self.setStatusBar(status_bar)


    def createToolbar(self) -> QToolBar:
        toolbar = QToolBar()

        import os
        print(os.system("pwd"))

        action = toolbar.addAction('load_hg')
        action.setIcon(QtGui.QIcon(str(Path('Resources/load.png'))))
        action.setText("Загрузить гиперграф")
        action.triggered.connect(self.centralWidget().loadHypergraphSlot)

        action = toolbar.addAction('save_hg')
        action.setIcon(QtGui.QIcon(str(Path('Resources/save.png'))))
        action.setText("Сохранить гиперграф")
        action.triggered.connect(self.centralWidget().saveHypergraphSlot)

        action = toolbar.addAction('new_scene')
        action.setIcon(QtGui.QIcon(str(Path('Resources/new.png'))))
        action.setText("Новый гиперграф")
        action.triggered.connect(self.centralWidget().resetSceneSlot)

        toolbar.addSeparator()

        action = toolbar.addAction('add_vertex')
        action.setIcon(QtGui.QIcon(str(Path('Resources/new_vertex.png'))))
        action.setText("Добавить вершину")
        action.triggered.connect(self.centralWidget().addVertexForCurrentSceneSlot)
        
        action = toolbar.addAction('remove_vertex')
        action.setIcon(QtGui.QIcon(str(Path('Resources/remove_vertex.png'))))
        action.setText("Удалить вершину")
        action.triggered.connect(self.centralWidget().removeVertexForCurrentSceneSlot)

        action = toolbar.addAction('add_edge')
        action.setIcon(QtGui.QIcon(str(Path('Resources/new_edge.png'))))
        action.setText("Добавить ребро")
        action.triggered.connect(self.centralWidget().addEdgeForCurrentSceneSlot)

        action = toolbar.addAction('remove_edge')
        action.setIcon(QtGui.QIcon(str(Path('Resources/remove_edge.png'))))
        action.setText("Удалить ребро ребро")
        action.triggered.connect(self.centralWidget().removeEdgeForCurrentSceneSlot)

        toolbar.addSeparator()

        action = toolbar.addAction('contraction_player')
        action.setIcon(QtGui.QIcon(str(Path('Resources/contraction.png'))))
        action.setText("Стягивание гиперграфа")
        action.triggered.connect(self.centralWidget().startContractionPlayerSlot)

        toolbar.addSeparator()

        action = toolbar.addAction('сontraction_2')
        action.setIcon(QtGui.QIcon(str(Path('Resources/contraction.png'))))
        action.setText("Cтягивание v2.0")
        action.triggered.connect(self.centralWidget().startContractionPlayerSlot2)

        return toolbar


