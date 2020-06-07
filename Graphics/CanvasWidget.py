import functools
from collections import Set
from pathlib import Path
from typing import List

from PyQt5.QtWidgets import QFileDialog, QGraphicsView, QToolBar, QMessageBox
from PyQt5 import QtCore

from Hypergraph import HyperGraph
from Graphics.CanvasHyperGraph import CanvasHyperGraph
from Vertex import Vertex


def filter_vertices(s: List, v: Vertex) -> Set:
    if v.id in ['a', 'b']:
        s.append(v)

    return s


def find_uniq_vertices(edges_lists):
    found_vertices = []

    for edges_list in edges_lists:
        for edge in edges_list:
            for vertex in edge.getVertices():
                if vertex not in found_vertices:
                    found_vertices.append(vertex)

    return found_vertices


def vertices_list_to_str(edge):
    vertice_ids = [v.id for v in edge.getVertices()]

    return ','.join(vertice_ids)


def update_denied(denied, edge):
    for vertex in edge.getVertices():
        if vertex.id not in denied:
            denied.append(vertex.id)


def get_ends(path, key):
    ends = []

    curr_vertices = None
    prev_vertices = None

    if not len(path):
        return []

    curr_vertices = path[-1].getVertices()
    prev_vertices = [v.id for v in path[-2].getVertices()] if len(path) > 2 else [key]

    for curr_v in curr_vertices:
        if curr_v.id not in prev_vertices:
            ends.append(curr_v.id)

    print('getEnds start')
    print(path[len(path) - 2].getVertices())
    print(ends)
    print('getEnds end')
    return ends


# noinspection PyPep8Naming
class CanvasWidget(QGraphicsView):

    def __init__(self, scene: CanvasHyperGraph):
        super().__init__(scene)
        self.setMouseTracking(True)

        self._createContractionToolbar()
        self._create_contraction_toolbar()

        self.cv2_history = []
        self.cv2_step = 0
        self.pairs = []

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

    def _create_contraction_toolbar(self):
        toolbar = QToolBar(parent=self)
        toolbar.setFloatable(True)
        toolbar.setMovable(True)
        toolbar.hide()

        action = toolbar.addAction('next')
        action.triggered.connect(self.next_hg2)
        action = toolbar.addAction('previous')
        action.triggered.connect(self.previous_hg2)
        action = toolbar.addAction('stop')
        action.triggered.connect(self.stopContractionPlayerSlot2)

        self.contraction_toolbar2 = toolbar

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
        contracted_vertex.setPos(average_pos / 2.)
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

    def startContractionPlayerSlot2(self):
        self.saved_scene = self.scene()

        start_hg = HyperGraph(other=self.saved_scene)
        self.contraction_toolbar2.show()

        chg = CanvasHyperGraph(start_hg)

        self.cv2_history.append(chg)
        self.cv2_step += 1

        for canvas_vertex in chg.vertices:
            if canvas_vertex.id in ['a', 'b']:
                print(canvas_vertex.id)
                canvas_vertex.set_as_pairing()

        self.pairs.append({
            'a': {
                'denied': [],
                'paths': []
            },
            'b': {
                'denied': [],
                'paths': []
            }
        })

        self.setScene(chg)

    def next_hg2(self):
        print('click next')
        hg = CanvasHyperGraph(self.cv2_history[self.cv2_step - 1])

        for pair in self.pairs:
            print('current pair', self.pairs.index(pair))
            for key in pair.keys():
                for vertex in hg.vertices:
                    if vertex.id is key:
                        vertex.set_as_pairing()

                print('current key', key)
                path_search = pair[key]

                denied = path_search['denied']
                paths = path_search['paths']

                print('\tprevious denied', denied)
                print('\tprevious paths', [[vertices_list_to_str(edge) for edge in path] for path in paths])

                path_indexes_to_remove = []
                new_paths = []

                if not len(paths):
                    new_paths = [[next_edge] for next_edge in hg.find_next_edges([key])]

                    for new_path in new_paths:
                        update_denied(denied, new_path[0])
                else:
                    for path in paths:
                        print('\tcurrent path', [vertices_list_to_str(edge) for edge in path])
                        ends = get_ends(path, key)
                        print('\tcurrent path ends', ends)
                        next_edges = hg.find_next_edges(ends, [vertex for vertex in denied if vertex not in ends])

                        if not len(next_edges):
                            path_indexes_to_remove.append(paths.index(path))
                        else:
                            first_next_edge = next_edges[0]

                            for next_edge in next_edges[1:]:
                                update_denied(denied, next_edge)
                                new_path = path.copy()
                                new_path.append(next_edge)
                                new_paths.append(new_path)

                            update_denied(denied, first_next_edge)
                            path.append(first_next_edge)

                if len(path_indexes_to_remove):
                    paths = [paths[i] for i in range(len(paths)) if i not in path_indexes_to_remove]

                paths.extend(new_paths)

                pair[key]['paths'] = paths
                pair[key]['denied'] = denied

                print(denied)
                print([[vertices_list_to_str(edge) for edge in path] for path in paths])

                for path in paths:
                    for edge in path:
                        edge.set_as_pairing_search_result()

        self.cv2_history.append(hg)
        self.cv2_step += 1

        self.setScene(hg)

    def previous_hg2(self):
        prev_hg = self.cv2_history[self.cv2_step - 2 if self.cv2_step > 1 else 0]
        self.cv2_step = (self.cv2_step - 1) if self.cv2_step > 0 else 0
        self.setScene(prev_hg)

    def stopContractionPlayerSlot2(self):
        self.contraction_toolbar2.hide()

        self.setScene(self.saved_scene)

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
