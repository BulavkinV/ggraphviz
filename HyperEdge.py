from Vertex import Vertex

class HyperEdge:

    def __init__(self, *vertices):
        if not vertices:
            raise ValueError("Vertices set can't be empty")

        self.vertices = set(vertices)

    def __str__(self):
        result = "Edge (%s)" % (','.join(map(str, self.vertices)))
        return result

    def getVertices(self):
        return self.vertices

    def addVertex(self, vertex:Vertex):
        self.vertices.add(vertex)

    def deleteVertex(self, vertex:Vertex):
        self.vertices -= {vertex}

    def replaceVertex(self, old:Vertex, new:Vertex):
        self.deleteVertex(old)
        self.addVertex(new)

    def getDegree(self):
        return len(self.vertices)