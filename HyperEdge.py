from __future__ import annotations
from enum import Enum, auto

from Vertex import Vertex

class HyperEdgeCrossingVariants(Enum):
    NOT_CROSSING = auto()
    CROSSING = auto()
    ONE_INSIDE_ANOTHER = auto()
    SAME = auto()

class HyperEdge:

    def __init__(self, *vertices, other:HyperEdge=None):
        if other:
            self._copy_constructor(other)
        elif vertices:
            self.vertices = set(vertices)
        else:
            raise ValueError("Vertices set can't be empty")
        

    def _copy_constructor(self, other:HyperEdge):
        self.vertices = other.vertices

    def __str__(self):
        result = "Edge (%s)" % (','.join(map(str, self.vertices)))
        return result

    def getVertices(self):
        return self.vertices

    def getDegree(self):
        return len(self.vertices)

    def getCrossingVariant(self, other:HyperEdge) -> HyperEdgeCrossingVariants:
        if self.vertices == other.vertices:
            return HyperEdgeCrossingVariants.SAME

        edge_crossing = self.vertices & other.vertices
        if not edge_crossing:
            return HyperEdgeCrossingVariants.NOT_CROSSING
        elif edge_crossing == self.vertices or edge_crossing == other.vertices:
            return HyperEdgeCrossingVariants.ONE_INSIDE_ANOTHER
        else:
            return HyperEdgeCrossingVariants.CROSSING

    def isHyperedge(self):
        return self.getDegree() > 2

    def isSimpleEdge(self):
        return self.getDegree() == 2

    def addVertex(self, vertex:Vertex):
        self.vertices.add(vertex)

    def deleteVertex(self, vertex:Vertex):
        self.vertices -= {vertex}

    def replaceVertex(self, old:Vertex, new:Vertex):
        self.deleteVertex(old)
        self.addVertex(new)
