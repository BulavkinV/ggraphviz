from math import pi, sin, cos

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
        
        self.real_point_gap = 30.

        self.default_pen = QtGui.QPen()
        self.setPen(self.default_pen)

        # if self.getDegree() == 2:
        #     vertices = list(self.getVertices())
        #     vertices[1].setPos(50., 0.)                
        #     path = QtGui.QPainterPath(vertices[0].pos())
        #     path.lineTo(vertices[1].pos())
        #     self.setPath(path)

    def setNewVertices(self, vertices:set):
        self.vertices = {v for v in vertices if v in self.vertices}

    def grahamConvex(self, all_vertices:set):
        self.setNewVertices(all_vertices)

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

    def getSupportConvex(self):
        if not self.convex:
            raise Exception()

        convex = [ (self.convex[i-1], self.convex[i], self.convex[(i+1) % len(self.convex)]) for i in range(len(self.convex)) ]
        support_convex = []
        for prev, vertex, next in convex:
            angles = []
            for v in (prev, next):
                a = vertex.polar_angle(v)
                angles.append(a)
            angle = sum(angles) /2.
            # TODO redo
            support_vertex = CanvasVertex(id = vertex.getId() + '\'')
            support_vertex.setPos(
                vertex.pos() + QtCore.QPointF(self.real_point_gap*cos(angle), self.real_point_gap*sin(angle))
            )
            if prev.vector_product(vertex, support_vertex) < 0.:
                angle += pi
                support_vertex.setPos(
                    vertex.pos() + QtCore.QPointF(self.real_point_gap*cos(angle), self.real_point_gap*sin(angle))
                )
            support_convex.append(support_vertex.pos())

        self.support_convex = support_convex

        return support_convex


    def draw(self):
        if not self.support_convex:
            raise Exception()

        path = QtGui.QPainterPath()

        path.moveTo(self.support_convex[0])
        for vertex in self.support_convex[1:]:
            path.lineTo(vertex)
            # path.quadTo()
        path.closeSubpath()

        self.setPath(path)


        return path
            