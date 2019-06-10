from PyQt5 import QtWidgets

class AddVertexDialog(QtWidgets.QInputDialog):

    def __init__(self):
        super().__init__()
        self.setModal(True)
        
        self.setWindowTitle("Создание новой вершины")
        self.setLabelText("Введите имя вершины")