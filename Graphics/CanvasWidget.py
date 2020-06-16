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


# def find_uniq_vertices(edges_lists):
#     found_vertices = []
#
#     for edges_list in edges_lists:
#         for edge in edges_list:
#             for vertex in edge.getVertices():
#                 if vertex not in found_vertices:
#                     found_vertices.append(vertex)
#
#     return found_vertices

def try_to_find_path(pair, node_keys):
    key_a = node_keys[0]
    key_b = node_keys[1]

    path_a_part = None
    path_b_part = None

    for path_a in pair[key_a]['paths']:
        last_edge_id = path_a[-1].id

        for path_b in pair[key_b]['paths']:
            if last_edge_id in [edge.id for edge in path_b]:
                path_a_part = path_a
                path_b_part = path_b
                break

        if path_a_part:
            break

    if path_a_part and path_b_part:
        pair['$path'] = path_a_part[:-1]
        pair['$path'].extend(path_b_part)

    print(pair['$path'])


def find_max_edge_order(edges):
    max_order = 0

    for edge in edges:
        edge_order = get_edge_order(edge)
        if edge_order > max_order:
            max_order = edge_order

    return max_order


def get_edge_order(edge):
    return len(edge.vertices)


def find_edges_with_lesser_order(edges, order):
    lesser_order_edges = []

    for i, edge in enumerate(edges):
        edge_order = get_edge_order(edge)

        if edge_order < order:
            lesser_order_edges.append((i, edge))

    return lesser_order_edges


def find_edges_with_order(edges, order):
    edge_tuples = []

    for i, edge in enumerate(edges):
        edge_order = get_edge_order(edge)

        if edge_order is order:
            edge_tuples.append((i, edge))

    return edge_tuples


def has_all_vertices(testing_edge, target_edge):
    for testing_vertex in testing_edge.vertices:
        target_edge_vertices_ids = [v.id for v in target_edge.vertices]

        if testing_vertex.id not in target_edge_vertices_ids:
            return False

    return True


def find_sub_edge_indexes(edges, super_edge):
    sub_edge_indexes = []

    sub_edges_tuples = find_edges_with_lesser_order(edges, get_edge_order(super_edge))
    print('\t\t\tsuper edge', super_edge)
    print('\t\t\tfound sub edges', [vertices_list_to_str(edge) for i, edge in sub_edges_tuples])

    for i, sub_edge in sub_edges_tuples:
        if has_all_vertices(sub_edge, super_edge):
            sub_edge_indexes.append(i)

    print('\t\t\tfound sub edge indexes', sub_edge_indexes)

    return sub_edge_indexes


def vertices_list_to_str(edge):
    return ','.join([v.id for v in edge.getVertices()])


def update_denied(denied, edge):
    for vertex in edge.getVertices():
        if vertex.id not in denied:
            denied.append(vertex.id)


def get_ends(path, key):
    ends = []

    if not len(path):
        print('\tfound ends', [])
        return []

    curr_vertices = path[-1].getVertices()
    prev_vertices = [v.id for v in path[-2].getVertices()] if len(path) > 2 else [key]

    for curr_v in curr_vertices:
        if curr_v.id not in prev_vertices:
            ends.append(curr_v.id)

    print('\tfound ends', ends)
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
        self.cv2_step = 0

        for canvas_vertex in chg.vertices:
            if canvas_vertex.id in ['a', 'b']:
                print(canvas_vertex.id)
                canvas_vertex.set_as_pairing()

        self.pairs.append({
            '$path': [],
            'a': {
                'denied': [],
                'paths': [],
            },
            'b': {
                'denied': [],
                'paths': []
            }
        })

        self.setScene(chg)

    def next_hg2(self):
        print('click next')

        history = self.cv2_history
        step = self.cv2_step

        if step < len(history) - 1:
            print('current step', step)
            self.setScene(history[step])
            return

        if not history[step - 1]:
            print('no step found')
            return

        hg = CanvasHyperGraph(history[step - 1])

        # for edge in hg.edges:
        #     edge.set_status()

        hg_edge_ids = [edge.id for edge in hg.edges]

        for pair in self.pairs:
            print('current pair', self.pairs.index(pair))

            pair_keys = [key for key in pair.keys() if key != '$path']

            try_to_find_path(pair, pair_keys)

            if len(pair['$path']):
                path_edge_ids = [edge.id for edge in pair['$path']]
                hg_path_edges = [edge for edge in hg.edges if edge.id in path_edge_ids]
                print('\tprotected path', [vertices_list_to_str(edge) for edge in pair['$path']])
                print('\thg has {}/{} edges'.format(len([edge.id for edge in pair['$path'] if edge.id in hg_edge_ids]), len(pair['$path'])))
                for edge in hg_path_edges:
                    edge.set_status('protected')
                    # edge.setPen(edge.protected_pen)
                    # edge.status = 'protected'
                    # edge.update()
                continue

            for key in pair_keys:
                for vertex in hg.vertices:
                    if vertex.id is key:
                        vertex.set_as_pairing()

                print('current key', key)

                denied = pair[key]['denied']
                paths = pair[key]['paths']

                print('\tprevious denied', denied)
                print('\tprevious paths', [[vertices_list_to_str(edge) for edge in path] for path in paths])

                path_indexes_to_remove = []
                new_paths = []

                if not len(paths):
                    new_paths = [[next_edge] for next_edge in hg.find_next_edges([key])]
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
                                new_path = path.copy()
                                new_path.append(next_edge)
                                new_paths.append(new_path)

                            path.append(first_next_edge)

                        print('\ttemp denied', denied)
                        print('\ttemp paths', [[vertices_list_to_str(edge) for edge in path] for path in paths])

                if len(path_indexes_to_remove):
                    paths = [paths[i] for i in range(len(paths)) if i not in path_indexes_to_remove]
                    path_indexes_to_remove = []

                for new_path in new_paths:
                    update_denied(denied, new_path[-1])

                paths.extend(new_paths)

                print('\tfound denied', denied)
                print('\tfound paths', [[vertices_list_to_str(edge) for edge in path] for path in paths])

                last_edges = [path[-1] for path in paths]

                max_edge_order = find_max_edge_order(last_edges)

                if max_edge_order > 2:
                    print('\tmax edge order', max_edge_order)

                    for i in range(max_edge_order):
                        order = max_edge_order - i

                        print('\t\tcurrent order', order)

                        super_edges = [edge for (_, edge) in find_edges_with_order(last_edges, order)]

                        print('\t\tedges with current order', super_edges)

                        for super_edge in super_edges:
                            path_indexes_to_remove.extend(find_sub_edge_indexes(last_edges, super_edge))
                            print(path_indexes_to_remove)
                            path_indexes_to_remove = list(set(path_indexes_to_remove))

                        print('\t\tsub edge indexes', path_indexes_to_remove)

                        if len(path_indexes_to_remove):
                            paths = [paths[j] for j in range(len(paths)) if j not in path_indexes_to_remove]

                pair[key]['paths'] = paths
                pair[key]['denied'] = denied

                print('\tfinal denied', denied)
                print('\tfinal paths', [[vertices_list_to_str(edge) for edge in path] for path in paths])

                for path in paths:
                    path_len = len(path)

                    for i, edge in enumerate(path):
                        print(edge.id, edge.id in hg_edge_ids)
                        new_status = 'found' if i < path_len - 1 else 'current'

                        for hg_edge in hg.edges:
                            if hg_edge == edge:
                                hg_edge.set_status(new_status)

        self.cv2_history.append(hg)
        self.cv2_step += 1

        for edge in hg.edges:
            print(edge.id, edge.status if edge.status else '__')

        self.setScene(hg)

    def previous_hg2(self):
        history = self.cv2_history
        step = self.cv2_step

        self.cv2_step = step - 1 if step else 0
        prev_hg = history[self.cv2_step]

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
