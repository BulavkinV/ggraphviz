from math import pi, sin, cos, isclose

from PyQt5 import QtWidgets, QtGui, QtCore

from Vertex import Vertex
from HyperEdge import HyperEdge

from Graphics.CanvasVertex import CanvasVertex

class CanvasHyperEdge(HyperEdge, QtWidgets.QGraphicsPathItem):
    
    def __init__(self, *vertices, **kwargs):
        # TODO redo

        QtWidgets.QGraphicsPathItem.__init__(self)
        
        if 'other' in kwargs:
            edge = kwargs.pop('other')
            if type(edge) == HyperEdge:
                vertices = {CanvasVertex(other=v) for v in edge.getVertices()}
                HyperEdge.__init__(self, *vertices)
            else:   
                HyperEdge.__init__(self, other=edge)
        else:
            vertices = {CanvasVertex(other=x) for x in vertices}
            HyperEdge.__init__(self, *vertices)
            # HyperEdge.__init__(self, *[CanvasVertex(vertex, self) for vertex in vertices], **kwargs)
        
        self.real_point_gap = 50.

        self.default_pen = QtGui.QPen()
        self.setPen(self.default_pen)

        self.hovered_pen = QtGui.QPen()
        self.hovered_pen.setColor(QtCore.Qt.red)

        self.hovered_brush = QtGui.QBrush()
        self.hovered_brush.setColor(QtCore.Qt.red)

        self.pairing_brush = QtGui.QBrush()
        self.pairing_brush.setColor(QtCore.Qt.green)

        self.default_brush = QtGui.QBrush()
        # self.score = 0
        self.setBrush(self.hovered_brush)

        self.support_convex = []
        self.setAcceptHoverEvents(True)
        self.multiplicity = 1

    def deleteVertex(self, vertex:CanvasVertex) -> None:
        HyperEdge.deleteVertex(self, vertex)
        for vertex in self.vertices:
            if type(vertex) is Vertex:
                return
        if self.getDegree() > 2:
            self.grahamConvex()
        
        self.draw()
        self.update()

    def equalPositions(self, other_vertices:set) -> bool:
        for v1 in self.vertices:
            for v2 in other_vertices:
                if v1 == v2:
                    if v1.pos() != v2.pos():
                        return False

        return True

    def updateVertices(self, vertices:set):
        if vertices == self.vertices and self.equalPositions(vertices):
            return

        self.vertices = {v for v in vertices if v in self.vertices}
        self.grahamConvex()

    def changeVertex(self, vertex:CanvasVertex, change_convex=True) -> None:
        self.vertices = {v for v in self.vertices if vertex != v}
        self.vertices.add(vertex)

        if change_convex:
            self.grahamConvex()
            if True:
                self.draw()

    def getMultiplicity(self) -> int:
        return  self.multiplicity

    def setMultiplicity(self, m:int) -> None:
        if self.multiplicity != m:
            self.multiplicity = m
            self.real_point_gap = 50. + 50.*(self.multiplicity - 1.)
            self.grahamConvex()
            self.draw()

    def grahamConvex(self):
        if not self.isHyperedge():
            return

        vertices = list(self.vertices)
        bottom_points = [vertices[0]]
        for vertex in vertices[1:]:
            if vertex.pos().y() < bottom_points[0].pos().y():
                bottom_points = [vertex]
            elif vertex.pos().y() == bottom_points[0].pos().y():
                bottom_points.append(vertex)
        
        if len(bottom_points) == 1:
            p0 = bottom_points[0]
        else:
            p0 = bottom_points[0]
            for vertex in bottom_points[1:]:
                if p0.pos().x() > vertex.pos().x():
                    p0 = vertex

        vertices.remove(p0)
        angles = [p0.polar_angle(v) for v in vertices]
        vertices = zip(vertices, angles)
        vertices = sorted(vertices, key = lambda x: x[1], reverse=True)

        # [ print(x.getId()) for x in vertices ]

        new_vertices = []
        continue_stack = 0
        for i, (vertex, angle) in enumerate(vertices[:-1]):
            if continue_stack:
                continue_stack -= 1
                continue
            
            elif angle == vertices[i+1][1]:

                same_angle_vertices = [vertices[i]]
                for j, (next_vertex, next_angle) in enumerate(vertices[i+1:], i+1):
                    if next_angle == angle:
                        same_angle_vertices.append(vertices[j])
                    else:
                        break
                
                same_angle_distances = [p0.distance(v[0]) for v in same_angle_vertices]
                further_distance = max(same_angle_distances)
                further_vertex = same_angle_vertices[same_angle_distances.index(further_distance)]

                new_vertices.append(further_vertex)
                continue_stack = len(same_angle_vertices) - 1
            else:    
                new_vertices.append(vertices[i])

        if not continue_stack:
            new_vertices.append(vertices[-1])

        vertices, angles = zip(*new_vertices)
        stack = [p0]
        stack += vertices[:2]
        for vertex in vertices[2:]:
            while stack[-2].vector_product(stack[-1], vertex) >= 0.:
                stack.pop()
            stack.append(vertex)

        self.convex = stack
        self.getSupportConvex()

        return stack 

    def inflateConvex(self, convex:list, gap:float) -> list:
        convex = [ (convex[i-1], convex[i], convex[(i+1) % len(convex)]) for i in range(len(convex)) ]

        result_convex = []
        for prev, vertex, next in convex:
            angles = []
            for v in (prev, next):
                a = CanvasVertex.polar_angle_pos(vertex, v)
                # a = vertex.polar_angle(v)
                angles.append(a)
            angle = sum(angles) /2.
            # TODO redo
            # new_vertex = CanvasVertex(id = vertex.getId() + '\'')
            new_vertex = QtCore.QPointF(
                vertex + QtCore.QPointF(gap*cos(angle), gap*sin(angle))
            )
            if CanvasVertex.vector_product_pos(prev, vertex, new_vertex) < 0.:
            # prev.vector_product(vertex, new_vertex) < 0.:
                angle += pi
                new_vertex = QtCore.QPointF(
                    vertex + QtCore.QPointF(gap*cos(angle), gap*sin(angle))
                )
            result_convex.append(new_vertex)

        return result_convex

    def intersectionOfSegmentAndCircle(self, center:QtCore.QPointF, radius:float, p1:QtCore.QPointF, p2:QtCore.QPointF):
        x0, y0 = center.x(), center.y()
        x1, y1 = p1.x(), p1.y()
        x2, y2 = p2.x(), p2.y()
        r = radius

        intercect1 = ((x0 - x2)*(x1 - x2) + (y0 - y2)*(y1 - y2) - (r**2*((x1 - x2)**2 + (y1 - y2)**2) - (-(x2*y0) - x0*y1 + x2*y1 + x1*(y0 - y2) + x0*y2)**2)**.5) / ((x1 - x2)**2 + (y1 - y2)**2)
        intercect2 = ((x0 - x2)*(x1 - x2) + (y0 - y2)*(y1 - y2) + (r**2*((x1 - x2)**2 + (y1 - y2)**2) - (-(x2*y0) - x0*y1 + x2*y1 + x1*(y0 - y2) + x0*y2)**2)**.5) / ((x1 - x2)**2 + (y1 - y2)**2)

        if isclose(intercect1, 1., abs_tol=1e-5) or isclose(intercect1, 0., abs_tol=1e-5):
            intercect = intercect2
        else:
            intercect = intercect1

        # intercect = max([intercect1, intercect2])
        # if abs(intercect) > 1.:
        #     print("Warning!")
        # intercect1 = (p1 + p2) * intercect1
        # intercect2 = (p1 + p2) * intercect2
        intercect = (p1 * intercect + (1.-intercect) * p2) 

        return intercect

        # if intercect1 in [p1, p2]:
        #     return intercect2
        # else:
        #     return intercect1 

    def getSupportConvex(self):
        if not self.convex:
            raise Exception()

        if not self.isHyperedge():
            raise Exception("Edge {} is not a hyperedge to create support convex for it!".format(self.getId())) 


        self.support_convex = self.inflateConvex([v.pos() for v in self.convex], self.real_point_gap)
        
        convex = [ (self.support_convex[i], self.support_convex[(i+1) % len(self.support_convex)]) for i in range(len(self.support_convex))]
        # distances = [CanvasVertex.distance_pos(v1, v2) for v1, v2 in convex]
        # self.arc_radius = 2.*max(distances)

        # quad_points = []
        # for v1, v2 in convex:
        #     quad_vertex = (v1 + v2)/2.
        #     quad_points.append(quad_vertex)
        # self.quad_points = self.inflateConvex(quad_points, 20.)

        # cubic1 = []
        # cubic2 = []
        # for v1, v2 in convex:
        #     c1 = (v1 + v2)/4.
        #     c2 = 3.*(v1 + v2)/4.
        #     cubic1.append(c1)
        #     cubic2.append(c2)
        
        # self.cubic_points = zip(self.inflateConvex(cubic1, 10.), self.inflateConvex(cubic2, 10.))

        arc_points = []
        convex = [ (self.support_convex[i-1], self.support_convex[i], self.support_convex[(i+1) % len(self.support_convex)]) for i in range(len(self.support_convex)) ]
        for i, (prev, current, next) in enumerate(convex):
            arc_points.append(self.intersectionOfSegmentAndCircle(self.convex[i], self.real_point_gap, prev, current))
            arc_points.append(current)
            arc_points.append(self.intersectionOfSegmentAndCircle(self.convex[i], self.real_point_gap, current, next))

        self.arc_points = arc_points
        
        return self.arc_points

    def draw(self, support_convex:bool=False):
        path = QtGui.QPainterPath()

        if self.getDegree() == 1:
            point = list(self.getVertices())[0].pos()
            start_angle = -pi / 4.
            c1 = point + QtCore.QPointF(self.real_point_gap*cos(start_angle), self.real_point_gap*sin(start_angle))
            start_angle -= pi /2.
            c2 = point + QtCore.QPointF(self.real_point_gap * cos(start_angle), self.real_point_gap * sin(start_angle))
            help_point = point + QtCore.QPointF(0, -self.real_point_gap)
            path.moveTo(point)
            path.quadTo(c1, help_point)
            path.quadTo(c2, point)

        elif self.getDegree() == 2:
            vertices = list(self.getVertices())
            if self.multiplicity > 1:
                if vertices[0].pos().y() < vertices[1].pos().y():
                    p_start = vertices[0].pos()
                    p_finish = vertices[1].pos()
                else:
                    p_start = vertices[1].pos()
                    p_finish = vertices[0].pos()

                distance = CanvasVertex.distance_pos(p_start, p_finish)
                base_angle = CanvasVertex.polar_angle_pos(p_start, p_finish)
                base_angle += pi/2.*(-1)**self.multiplicity
                c = (p_start + p_finish) / 2. + QtCore.QPointF(distance/2.*self.multiplicity/2.*cos(base_angle), distance/2.*self.multiplicity/2.*sin(base_angle))
                path.moveTo(p_start)
                path.quadTo(c, p_finish)
            else:
                path.moveTo(vertices[0].pos())
                path.lineTo(vertices[1].pos())
        else:
            if not self.support_convex:
                self.grahamConvex()

            path.moveTo(self.arc_points[0])
            for center, arc_final, next in zip(self.arc_points[1::3], self.arc_points[2::3], self.arc_points[3::3]):
                path.quadTo(center, arc_final)
                path.lineTo(next)

            path.quadTo(self.arc_points[-2], self.arc_points[-1])
            path.closeSubpath()

            if support_convex:
                path.moveTo(self.support_convex[0])
                for vertex in self.support_convex[1:]:
                    path.lineTo(vertex)
                path.closeSubpath()

        self.setPath(path)

        return path
        # quad
        # path.moveTo(self.support_convex[0])
        # for vertex, quad in zip(self.support_convex[1:], self.quad_points[:-1]):
        #     # path.lineTo(vertex)
        #     path.quadTo(quad, vertex)
        # path.quadTo(self.quad_points[-1], self.support_convex[0])
        # path.closeSubpath()

        # cubic
        # path.moveTo(self.support_convex[0])
        # cubic1, cubic2 = zip(*self.cubic_points)
        # for vertex, c1, c2 in zip(self.support_convex[1:], cubic1[:-1], cubic2[:-1]):
        #     # path.lineTo(vertex)
        #     path.cubicTo(c1, c2, vertex)
        # path.cubicTo(cubic1[-1], cubic2[-1], self.support_convex[0])
        # path.closeSubpath()

    #QT reimplimentations
    # def boundingRect(self):
        
    #     if self.isSimpleEdge():
    #         pass

    #     return QtWidgets.QGraphicsPathItem.boundingRect(self)

    def setSelected(self, selected:bool):
        QtWidgets.QGraphicsPathItem.setSelected(self, selected)
        if selected:
            self.setPen(self.hovered_pen)
        else:
            self.setPen(self.default_pen)
        
        self.update()

    # mouse evnets
    # def hoverEnterEvent(self, mouseEvent:QtWidgets.QGraphicsSceneHoverEvent):
    #     self.setSelected(True)
    #     QtWidgets.QGraphicsPathItem.hoverEnterEvent(self, mouseEvent)

    # def hoverLeaveEvent(self, mouseEvent:QtWidgets.QGraphicsSceneHoverEvent):
    #     self.setSelected(False)
    #     QtWidgets.QGraphicsPathItem.hoverLeaveEvent(self, mouseEvent)


    # DEPRECATED
    def calculateCenter(self):
        vertices_pos = [v.pos() for v in self.vertices]
        self.center = vertices_pos[0]
        for vertex in vertices_pos[1:]:
            self.center += vertex
        
        return self.center

    def setScore(self, score:int):
        self.score = score
    
    def getScore(self):
        return self.score