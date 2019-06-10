from PyQt5.QtWidgets import QMainWindow, QDesktopWidget, QToolBar, QStatusBar

from Graphics.CanvasWidget import CanvasWidget

class MainWindow(QMainWindow):
    
    def __init__(self, hg_canvas):
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
        action = toolbar.addAction('add_vertex')
        action.triggered.connect(self.centralWidget().scene().addVertexSlot)
        
        action = toolbar.addAction('remove_vertex')
        action.triggered.connect(self.centralWidget().scene().removeVertexSlot)

        action = toolbar.addAction('add_edge')
        action.triggered.connect(self.centralWidget().scene().addEdgeSlot)

        action = toolbar.addAction('remove_edge')
        action.triggered.connect(self.centralWidget().scene().removeEdgeSlot)

        return toolbar