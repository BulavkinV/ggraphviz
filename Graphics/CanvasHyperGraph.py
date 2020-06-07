import random
import copy
from math import pi, sin, cos
from enum import Enum, auto
import logging

from PyQt5 import QtWidgets, QtGui, QtCore

from Graphics.CanvasHyperEdge import CanvasHyperEdge
from Graphics.CanvasVertex import CanvasVertex

from Hypergraph import HyperGraph
from HyperEdge import HyperEdgeCrossingVariants


class SceneModes(Enum):
    NONE = auto()
    ADD_NEW_VERTEX = auto()
    REMOVE_VERTEX = auto()
    ADD_NEW_EDGE = auto()
    REMOVE_EDGE = auto()


class CanvasHyperGraph(QtWidgets.QGraphicsScene, HyperGraph):

    # initial procedures
    def __init__(self, hypergraph: HyperGraph = None, **kwargs):
        QtWidgets.QGraphicsScene.__init__(self)

        self.logger = logging.getLogger("hypergraph_logger")
        self.logger.setLevel(logging.DEBUG)

        if hypergraph:
            HyperGraph.__init__(self, other=hypergraph)
        else:
            HyperGraph.__init__(
                self,
                edges=kwargs.pop('edges', []),
                vertices=kwargs.pop('vertices', set())
            )

        self.edge_len = 100.
        self.scene_square_per_point = 1e4

        self.vertices = {CanvasVertex(other=x) for x in self.vertices}
        self.edges = [CanvasHyperEdge(other=x) for x in self.edges]

        self.initSceneRect()
        self.initialVertexPlacement()
        self.updateEdges()
        self.verticesVersusEdgesDict()
        self.placeVertices()

        # self.generateStructureGraph()
        # self.calculateCrossingMatrix()
        # self.rankEdges()

        # self.initialVerticesPlacement()
        # for edge in self.edges:
        #     print(edge.getScore())

        # TODO vertices placing

        # self.edges = [CanvasHyperEdge(x, self.vertices) for x in hg.getEdges()]

        self.calculateEdgesMultiplicity()
        self.updateEdges()
        self.drawEdges()

        self.selected_vertex = None
        self.selected_vertex_edges = []
        self.selected_vertices = []
        self.mode = SceneModes.NONE

    def initSceneRect(self):
        return
        if self.vertices:
            square = len(self.vertices) * self.scene_square_per_point
            scene_side = square ** .5
            self.setSceneRect(0., 0., scene_side, scene_side)

    # mode operations
    def setMode(self, mode: SceneModes) -> None:
        self.mode = mode

    def getMode(self) -> SceneModes:
        return self.mode

    # simple operations
    def getEdgeById(self, id: str) -> CanvasHyperEdge:
        for edge in self.edges:
            if id == edge.getId():
                return edge

        raise AttributeError

    def getEdgesById(self, ids: list) -> list:
        result = []
        for id in ids:
            result.append(self.getEdgeById(id))

        return result

    def getVertexById(self, id: str) -> CanvasVertex:
        for vertex in self.vertices:
            if vertex.getId() == id:
                return vertex

        raise AttributeError

    def exchangeEdges(self, edges: list) -> None:
        for i, edge in enumerate(self.edges):
            if edge in edges:
                self.removeItem(edge)
                self.edges[i] = edge
                self.addItem(self.edges[i])

    # correct vertex placement
    def initialVertexPlacement(self):
        left = 0.  # self.sceneRect().left()
        right = self.scene_square_per_point ** .5  # self.sceneRect().right()
        for vertex in self.vertices:
            vertex.setPos(QtCore.QPointF(random.uniform(left, right), random.uniform(left, right)))
            vertex.setZValue(1)
            self.addItem(vertex)

    def verticesVersusEdgesDict(self):
        self.verticesVersusEdges = {}
        for vertex in self.vertices:
            self.verticesVersusEdges[vertex.getId()] = [e.getId() for e in self.edges if vertex in e.getVertices()]

    def placeVertices(self):
        any_placement = True
        while any_placement:
            any_placement = False

            for vertex in self.vertices:
                # print("Point:", vertex.getId())
                pos = vertex.pos()
                edges_ids = self.verticesVersusEdges[vertex.getId()]
                # print("Edge:", edges_ids[0])
                # friendly_centers = [ mass_centers[id] for id in edges_ids ]
                # print(self.getVertexById('2').pos(), self.getVertexById('3').pos(), pos, friendly_centers[0])

                friendly_vertices = [e.getVertices() for e in [self.getEdgeById(id) for id in edges_ids]]
                friendly_vertices_set = set()
                for vers in friendly_vertices:
                    friendly_vertices_set |= set(vers)
                friendly_vertices = friendly_vertices_set

                # hostile_centers = {e for e in [edge.getId() for edge in self.edges] if e not in edges_ids}
                hostile_vertices = self.vertices - friendly_vertices - {
                    vertex}  # set(self.verticesVersusEdges.keys()) - friendly_vertices

                friendly_vertices = friendly_vertices_set - {vertex}

                new_pos = QtCore.QPointF(0., 0.)
                for fc in friendly_vertices:
                    # TODO / len(edge)
                    modulus = CanvasVertex.distance_pos(fc.pos(), pos) - self.edge_len
                    # print(fc.pos(), pos)
                    new_pos += (fc.pos() - pos) * modulus / CanvasVertex.distance_pos(fc.pos(), pos)

                for fc in hostile_vertices:
                    # (fc - pos)*modulus
                    if CanvasVertex.distance_pos(fc.pos(), pos) < self.edge_len:
                        modulus = CanvasVertex.distance_pos(fc.pos(), pos) - self.edge_len
                    else:
                        continue
                    # angle = CanvasVertex.polar_angle_pos(fc.pos(), pos)
                    print(fc.pos(), pos)
                    new_pos += (fc.pos() - pos) * modulus / CanvasVertex.distance_pos(fc.pos(), pos)

                self.placeVertex(vertex, pos + new_pos)
                if CanvasVertex.distance_pos(pos, pos + new_pos) > self.edge_len / 2.:
                    any_placement = True

                self.updateEdges()

        # self.updateEdges()

    # events
    def mousePressEvent(self, mouseEvent: QtWidgets.QGraphicsSceneMouseEvent) -> None:
        if self.mode is SceneModes.NONE:
            item = self.itemAt(mouseEvent.scenePos(), QtGui.QTransform())
            if type(item) is QtWidgets.QGraphicsEllipseItem:
                self.selected_vertex = item.parentItem()
                edges_ids = self.verticesVersusEdges[self.selected_vertex.getId()]
                self.selected_vertex_edges = self.getEdgesById(edges_ids)
                self.selectEdges(self.selected_vertex_edges)

        elif self.mode is SceneModes.REMOVE_VERTEX:
            items = self.items(mouseEvent.scenePos())
            vertex = [v for v in items if isinstance(v, QtWidgets.QGraphicsEllipseItem)]
            if vertex:
                vertex = vertex.pop().parentItem()
                self.removeVertex(vertex)
                self.setMode(SceneModes.NONE)

        elif self.mode is SceneModes.ADD_NEW_EDGE:
            items = self.items(mouseEvent.scenePos())
            vertex = [v for v in items if isinstance(v, QtWidgets.QGraphicsEllipseItem)]
            if vertex:
                vertex = vertex.pop().parentItem()
                vertex.setSelected(True)
                self.selected_vertices.append(vertex)

        elif self.getMode() is SceneModes.REMOVE_EDGE:
            item = self.itemAt(mouseEvent.scenePos(), QtGui.QTransform())
            if isinstance(item, CanvasHyperEdge):
                self.removeEdge(item)
                self.setMode(SceneModes.NONE)

    def mouseMoveEvent(self, mouseEvent: QtWidgets.QGraphicsSceneMouseEvent) -> None:
        # QtWidgets.QGraphicsScene.mouseMoveEvent(self, mouseEvent)
        # QtWidgets.QToolTip.hideText()
        items = self.items(mouseEvent.scenePos())

        if self.mode is SceneModes.NONE:
            selected_edges = [e for e in items if isinstance(e, CanvasHyperEdge)]

            if self.selected_vertex:
                new_edges = [e for e in selected_edges if e not in self.selected_vertex_edges]
                if new_edges:
                    if len(new_edges) > 1:
                        format_string = "Добавить вершину '{}' к рёбрам {}?".format(self.selected_vertex.getId(),
                                                                                    ','.join(map(str, new_edges)))
                    else:
                        format_string = "Добавить вершину '{}' к рёбру {}?".format(self.selected_vertex.getId(),
                                                                                   str(new_edges[0]))
                    QtWidgets.QToolTip.showText(mouseEvent.screenPos(), format_string, mouseEvent.widget())
                else:
                    QtWidgets.QToolTip.hideText()
                selected_edges = self.selected_vertex_edges + new_edges
                self.placeVertex(self.selected_vertex, mouseEvent.scenePos())
            self.selectEdges(selected_edges)
            # elif type(item) is QtWidgets.QGraphicsEllipseItem:
            #     selected_edges += [e for e in self.items(mouseEvent.scenePos()) if isinstance(e, CanvasHyperEdge) and e not in selected_edges]


        elif self.mode is SceneModes.ADD_NEW_VERTEX:
            self.selected_vertex.setPos(mouseEvent.scenePos())
            edges = [e for e in items if isinstance(e, CanvasHyperEdge)]
            if edges:
                if len(edges) > 1:
                    format_string = "Добавить новую вершину к рёбрам {}?".format(','.join(map(str, edges)))
                else:
                    format_string = "Добавить новую вершину к рёбру {}?".format(str(edges[0]))
                QtWidgets.QToolTip.showText(mouseEvent.screenPos(), format_string, mouseEvent.widget())
            else:
                QtWidgets.QToolTip.hideText()
            self.selected_vertex_edges = edges
            self.selectEdges(edges)

        elif self.getMode() is SceneModes.REMOVE_EDGE:
            selected_edges = [e for e in items if isinstance(e, CanvasHyperEdge)]
            self.selectEdges(selected_edges)

        QtWidgets.QGraphicsScene.mouseMoveEvent(self, mouseEvent)

    def mouseReleaseEvent(self, mouseEvent: QtWidgets.QGraphicsSceneMouseEvent) -> None:
        if self.mode is SceneModes.NONE:
            if self.selected_vertex:
                # Если вершина опущена над рёбрами нужно добавлять её в эти рёбра (через диалог)
                selected_edges = [e for e in self.items(mouseEvent.scenePos()) if isinstance(e, CanvasHyperEdge)]
                new_edges = [e for e in selected_edges if e not in self.selected_vertex_edges]
                if new_edges:
                    for edge in new_edges:
                        edge.addVertex(self.selected_vertex)
                        self.verticesVersusEdges[self.selected_vertex.getId()].append(edge.getId())

                self.placeVertex(self.selected_vertex, self.selected_vertex.pos())

            self.selected_vertex = None

        elif self.mode is SceneModes.ADD_NEW_VERTEX:
            success = False
            while not success:
                text, success = QtWidgets.QInputDialog.getText(mouseEvent.widget(), "Создание новой вершины",
                                                               "Введите имя вершины:")
                if success:
                    if not text:
                        msgBox = QtWidgets.QMessageBox(mouseEvent.widget())
                        msgBox.setText("Невозможно создать вершину с пустым именем!")
                        msgBox.exec()
                        success = False
                        continue
                    new_vertex = CanvasVertex(id=text)
                    if new_vertex in self.vertices:
                        msgBox = QtWidgets.QMessageBox(mouseEvent.widget())
                        msgBox.setText("Вершина с именем {} уже существует".format(new_vertex.getId()))
                        msgBox.exec()
                        success = False
                        continue

                    new_vertex.setPos(mouseEvent.scenePos())

                    self.addNewVertex(new_vertex, self.selected_vertex_edges)
                    self.removeItem(self.selected_vertex)

                    self.selected_vertex = None
                    self.selected_vertex_edges = []
                    self.setMode(SceneModes.NONE)
                else:
                    break

    def mouseDoubleClickEvent(self, mouseEvent: QtWidgets.QGraphicsSceneMouseEvent) -> None:
        if self.mode is SceneModes.NONE:
            items = self.items(mouseEvent.scenePos())
            vertex_to_rename = None
            for item in items:
                if isinstance(item, CanvasVertex):
                    vertex_to_rename = item
                elif isinstance(item.parentItem(), CanvasVertex):
                    vertex_to_rename = item.parentItem()

                if vertex_to_rename:
                    self.logger.debug("Item {} grabs DoubleClickEvent.".format(vertex_to_rename))
                    break

            if vertex_to_rename:
                success = False
                while not success:
                    text, success = QtWidgets.QInputDialog.getText(mouseEvent.widget(),
                                                                   "Переименование вершины {}".format(
                                                                       vertex_to_rename.getId()),
                                                                   "Введите новое имя вершины {}:".format(
                                                                       vertex_to_rename.getId()))

                    if not success:
                        break

                    if success:
                        text = text.strip()

                    if success and not text:
                        success = False

                    if text == vertex_to_rename.getId():
                        break

                    if success and text in [vertex.getId() for vertex in self.vertices]:
                        msgBox = QtWidgets.QMessageBox(mouseEvent.widget())
                        msgBox.setText("Вершина с именем {} уже существует!".format(text))
                        msgBox.exec()
                        success = False
                        continue

                    if success:
                        # edges = self.getEdgesById(self.verticesVersusEdges[vertex_to_rename.getId()])
                        # self.removeVertex(vertex_to_rename)
                        # vertex_to_rename.setId(text)

                        # self.addNewVertex(vertex_to_rename, edges)
                        self.renameVertex(vertex_to_rename, text)

    def keyPressEvent(self, keyEvent: QtGui.QKeyEvent) -> None:
        if self.getMode() is SceneModes.ADD_NEW_EDGE:
            if keyEvent.key() in [QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return]:
                if len(self.selected_vertices) >= 1:
                    self.addNewEdge(self.selected_vertices)
                    for vertex in self.selected_vertices:
                        vertex.setSelected(False)
                    self.selected_vertices = []
                    self.setMode(SceneModes.NONE)

        QtWidgets.QGraphicsScene.keyPressEvent(self, keyEvent)
        print(list(map(lambda x: x.getId(), self.vertices)))

    def selectEdges(self, edges: list) -> None:
        for edge in self.edges:
            if edge in edges:
                edge.setSelected(True)
            else:
                edge.setSelected(False)

    def calculateEdgeCenters(self):
        result = {}
        for edge in self.edges:
            result[edge.getId()] = edge.calculateCenter()

        return result

    def updateEdges(self):
        for edge in self.edges:
            edge.updateVertices(self.vertices)

    def initialVerticesPlacement(self):
        scores = [x.getScore() for x in self.edges]
        index = scores.index(max(scores))

        # intersect_indices = [ i for i, x in enumerate(map(lambda x: x in [HyperEdgeCrossingVariants.CROSSING, HyperEdgeCrossingVariants.ONE_INSIDE_ANOTHER, HyperEdgeCrossingVariants.SAME], self.crossing_matrix[index])) if x]

        # self.placeEdgeVertices(self.edges[index], QtCore.QPointF(0., 0.))

        open = [index]
        closed = []

        pos = QtCore.QPointF(0., 0.)
        while open:
            scores = [x.getScore() for x in [self.edges[i] for i in open]]
            max_score_index = scores.index(max(scores))
            index = open[max_score_index]
            del open[max_score_index]

            self.placeEdgeVertices(self.edges[index], pos)
            pos += QtCore.QPointF(200., 0.)

            intersect_indices = [i for i, x in enumerate(map(
                lambda x: x in [HyperEdgeCrossingVariants.CROSSING, HyperEdgeCrossingVariants.ONE_INSIDE_ANOTHER,
                                HyperEdgeCrossingVariants.SAME], self.crossing_matrix[index])) if x]
            intersect_indices = [x for x in intersect_indices if x not in open + closed]

            open += intersect_indices

            closed.append(index)

            if not open and len(closed) != len(self.edges):
                # TODO take best vertex from closed to open
                pass

    def calculateEdgesMultiplicity(self):
        self.same_edges = {edge.getId(): [] for edge in self.edges}
        for edge in self.edges:
            list_of_same_edges = [e.getId() for e in self.edges if edge.getVertices() == e.getVertices() and edge != e]
            self.same_edges[edge.getId()] = list_of_same_edges

        excluded_edges_ids = []
        for edge_id, same_edges_ids in self.same_edges.items():
            if same_edges_ids and edge_id not in excluded_edges_ids:
                factor = 2
                for increase_multiplicity_edge_id in same_edges_ids:
                    increase_multiplicity_edge = self.getEdgeById(increase_multiplicity_edge_id)
                    increase_multiplicity_edge.setMultiplicity(factor)
                    factor += 1
                    excluded_edges_ids.append(increase_multiplicity_edge_id)
            excluded_edges_ids.append(edge_id)

    def regularPolygon(self, n: int, start_point: QtCore.QPointF):
        points = [start_point]
        internal_angle = (n - 2.) * pi / n
        prev_point = start_point

        angle = pi - internal_angle / 2.
        angle = (pi * n + 2. * pi) / (2 * n)
        delta_angle = 2. * pi / n
        for i in range(1, n):
            points.append(
                QtCore.QPointF(
                    # cos(internal_angle) * prev_point.x() - sin(internal_angle) * prev_point.y(),
                    # sin(internal_angle) * prev_point.x() + cos(internal_angle) * prev_point.x()
                    prev_point.x() + self.edge_len * cos(angle),
                    prev_point.y() + self.edge_len * sin(angle)
                )
            )
            angle += delta_angle
            prev_point = points[-1]

        print('\n'.join([str(p) for p in points]))

        return points

    def placeEdgeVertices(self, edge: CanvasHyperEdge, start_position: QtCore.QPointF):
        points = list(edge.getVertices())
        if edge.isSimpleEdge():
            if points[0].isPlaced():
                if not points[1].isPlaced():
                    #     self.placeVertex(points[0], start_position)
                    #     self.placeVertex(points[1], start_position + QtCore.QPointF(100., 0))
                    # else:
                    self.placeVertex(points[1], points[0].pos() + QtCore.QPointF(100., 0))

            else:
                if points[1].isPlaced():
                    self.placeVertex(points[0], points[1].pos() + QtCore.QPointF(100., 0))
                else:
                    self.placeVertex(points[0], start_position)
                    self.placeVertex(points[1], start_position + QtCore.QPointF(100., 0))

        else:

            positions = self.regularPolygon(edge.getDegree(), start_position)
            for point, pos in zip(points, positions):
                self.placeVertex(point, pos)

        edge.updateVertices(self.vertices)

    def placeVertex(self, vertex: CanvasVertex, pos: QtCore.QPointF):
        self.removeItem(vertex)
        self.vertices -= {vertex}

        vertex.setPos(pos)
        edges = self.getEdgesById(self.verticesVersusEdges[vertex.getId()])
        [edges[i].changeVertex(vertex) for i in range(len(edges))]
        self.exchangeEdges(edges)

        self.vertices |= {vertex}
        self.addItem(vertex)
        # for item in self.items():
        #     if type(item) is CanvasVertex and item == vertex:
        #         item.setPos(pos)

    def exchangeVertices(self, v1: CanvasVertex, v2: CanvasVertex):
        pass

    def drawVertices(self, vertices: set()):
        for vertex in vertices:
            self.drawVertex(vertex)

    def drawVertex(self, vertex: CanvasVertex):
        if vertex in filter(lambda item: isinstance(item, CanvasVertex), self.items()):
            return
        while True:
            vertex.setX(random.randint(0, 100))
            vertex.setY(random.randint(0, 100))
            if not self.collidingItems(vertex):
                break

        self.addItem(
            vertex
        )

    def drawEdges(self):
        for edge in self.edges:
            edge.updateVertices(self.vertices)
            edge.draw()
            self.addItem(edge)

            # for i, item in enumerate(support_convex):
            #     vertex = CanvasVertex(id=str(i)+ '!')
            #     vertex.setPos(item)
            #     self.addItem(vertex)

    def drawEdge(self, edge: CanvasHyperEdge):
        self.addItem(edge)

    def addVertex(self, vertex: CanvasVertex, edge: CanvasHyperEdge = None):
        super().addVertex(vertex, edge)
        self.addItem(vertex)

    def addNewVertex(self, vertex: CanvasVertex, edges: list = None) -> None:
        self.vertices.add(vertex)
        if edges:
            for edge in edges:
                edge.addVertex(vertex)

        self.verticesVersusEdges[vertex.getId()] = [edge.getId() for edge in edges] if edges else []
        vertex.setZValue(1)
        self.addItem(vertex)
        self.placeVertex(vertex, vertex.pos())

    def removeVertex(self, vertex: CanvasVertex) -> None:
        self.removeItem(vertex)
        self.vertices -= {vertex}
        self.verticesVersusEdges.pop(vertex.getId())
        edges_to_remove = []
        for edge in self.edges:
            if vertex in edge.getVertices():
                if edge.isSimpleEdge():
                    edges_to_remove.append(edge)
                else:
                    # TODO need to redraw
                    edge.deleteVertex(vertex)

        for edge in edges_to_remove:
            self.removeEdge(edge)

    def addNewEdge(self, vertices: set) -> None:
        edge = CanvasHyperEdge(*vertices)

        # checking for same_edges
        same_edges = []
        for e in self.edges:
            if edge.compareByVertices(e):
                same_edges.append(e.getId())
        if same_edges:
            edge.setMultiplicity(len(same_edges) + 1)
            for same_edge_id in same_edges:
                self.same_edges[same_edge_id].append(edge.getId())

        self.same_edges[edge.getId()] = same_edges

        self.edges.append(edge)
        for vertex in list(vertices):
            self.verticesVersusEdges[vertex.getId()].append(edge.getId())

        edge.draw()
        self.addItem(edge)

    def removeEdge(self, edge: CanvasHyperEdge) -> None:
        edge_id = edge.getId()

        # check for same edges
        if self.same_edges[edge_id]:
            multiplicity = edge.getMultiplicity()
            for other_same_edge_id in self.same_edges[edge_id]:
                other_same_edge = self.getEdgeById(other_same_edge_id)
                if other_same_edge.getMultiplicity() > multiplicity:
                    other_same_edge.setMultiplicity(other_same_edge.getMultiplicity() - 1)
                self.same_edges[other_same_edge_id].remove(edge_id)

        self.same_edges.pop(edge_id)

        for l in self.verticesVersusEdges.values():
            if edge_id in l:
                l.remove(edge_id)
        self.edges.remove(edge)
        self.removeItem(edge)

    def renameVertex(self, vertex: CanvasVertex, new_id: str) -> None:
        old_id = vertex.getId()

        # for edge_id in self.verticesVersusEdges[old_id]:
        #     edge = self.getEdgeById(edge_id)
        #     edge.renameVertex(old_id, new_id)

        self.verticesVersusEdges[new_id] = self.verticesVersusEdges[old_id]
        self.verticesVersusEdges.pop(old_id)

        vertex.setId(new_id)

        # self.removeItem(vertex)
        # self.vertices -= {vertex}

        # edges = self.getEdgesById(self.verticesVersusEdges[vertex.getId()])
        # vertex.setId(new_id)
        # [edges[i].changeVertex(vertex) for i in range(len(edges))]
        # self.exchangeEdges(edges)

        # self.vertices |= {vertex}
        # self.addItem(vertex)

    def addVertices(self, vertices: set, edge: CanvasHyperEdge = None):
        for vertex in vertices:
            self.addVertex(vertex, edge)

    def addEdge(self, edge: CanvasHyperEdge):
        edge = CanvasHyperEdge(other=edge)
        super().addEdge(edge)
        # self.drawEdge(edge)

    def addEdges(self, edges):
        edges = [CanvasHyperEdge(edge=edge) for edge in edges]
        super().addEdges(edges)
        # self.drawEdges(edges)

    def update(self, rect=QtCore.QRectF()):
        print('update')
        super().update(rect)

    # QT slots
    def addVertexSlot(self):
        self.setMode(SceneModes.ADD_NEW_VERTEX)
        vertex_width = 10.
        vertex_height = 10.

        vertex_ellipse_rect = QtCore.QRectF(
            -vertex_width / 2., -vertex_height / 2,
            vertex_width, vertex_height
        )
        ellipse_default_brush = QtGui.QBrush(QtCore.Qt.green)
        point = QtWidgets.QGraphicsEllipseItem(vertex_ellipse_rect)
        point.setBrush(ellipse_default_brush)
        self.selected_vertex = point
        self.addItem(point)

    def removeVertexSlot(self):
        self.setMode(SceneModes.REMOVE_VERTEX)

    def addEdgeSlot(self):
        self.setMode(SceneModes.ADD_NEW_EDGE)

    def removeEdgeSlot(self):
        self.setMode(SceneModes.REMOVE_EDGE)

    # DEPRECATED
    def calculateCrossingMatrix(self):
        # checking crossing variants
        self.crossing_matrix = [[False] * len(self.edges) for _ in range(len(self.edges))]
        for i, edge in enumerate(self.edges[:-1]):
            for j, other in enumerate(self.edges[i + 1:], i + 1):
                self.crossing_matrix[i][j] = edge.getCrossingVariant(other)

        # matrix reflection
        for i in range(len(self.crossing_matrix)):
            for j in range(i):
                self.crossing_matrix[i][j] = self.crossing_matrix[j][i]

        # # reflection test
        # for i in range(len(self.crossing_matrix)):
        #     for j in range(len(self.crossing_matrix)):
        #         assert self.crossing_matrix[i][j] == self.crossing_matrix[j][i], "Bad reflection"

    def rankEdges(self, sort=False):
        for i, edge in enumerate(self.edges):
            rank = 0
            if edge.isHyperedge():
                rank += 5
                rank += edge.getDegree() - 3
            else:
                rank += 2

            crossing_variants = self.crossing_matrix[i]
            for j, variant in enumerate(crossing_variants):
                if variant is HyperEdgeCrossingVariants.CROSSING:
                    rank += edge.getCrossingDegree(self.edges[j])
                elif variant is HyperEdgeCrossingVariants.SAME:
                    rank += 2
                elif variant is HyperEdgeCrossingVariants.ONE_INSIDE_ANOTHER:
                    rank += 1

            edge.setScore(rank)

        if sort:
            self.edges.sort(key=lambda x: x.getScore(), reverse=True)

    # def render(self, *args, **kwargs):
    #     # print("render")
    #     # self.drawVertices()
    #     super().render(*args, **kwargs)
