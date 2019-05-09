from PyQt5.QtWidgets import QMainWindow, QDesktopWidget

from Graphics.CanvasWidget import CanvasWidget

class MainWindow(QMainWindow):
    
    def __init__(self, hg_canvas):
        self.minimum_size = (800, 600)

        super().__init__()
        
        desktop = QDesktopWidget()
        self.setMinimumSize(*self.minimum_size)
        self.move(
            desktop.width() // 2 - self.minimum_size[0] // 2, 
            desktop.height() // 2 - self.minimum_size[1] // 2)
        self.setWindowTitle("Визуализация гиперграфов")
        
        # add menu bar
        # add toolbar
        # status bar


        self.setCentralWidget(CanvasWidget(hg_canvas))