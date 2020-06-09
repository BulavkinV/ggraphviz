from uuid import uuid4

from Vertex import Vertex
from HyperEdge import HyperEdge


class ComplexVertex(Vertex):

    def __init__(self, *vertices):
        num_of_verts = len(vertices)
        if num_of_verts > 2:
            raise ValueError("ComplexVertex can't be constructed from more than two vertices!")

        if num_of_verts == 1:
            self.v = vertices[0]
        else:
            self.v1 = vertices[0]
            self.v2 = vertices[1]

        super().__init__(uuid4())

    def toEdge(self):
        if hasattr(self, 'v1') and hasattr(self, 'v2'):
            return HyperEdge(self.v1, self.v2)
        else:
            raise ValueError("Impossible to construct edge from one vertex!")
