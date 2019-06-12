from __future__ import annotations
from collections import namedtuple
import json
from pathlib import Path

from Vertex import Vertex
from HyperEdge import HyperEdge
from ComplexVertex import ComplexVertex


class HyperGraph():
    """
        TODO: desiarization from JSON
    """

    def __init__(self, vertices:set=None, edges:list=None, other:HyperGraph=None):
        # TODO check arguments
        if other:
            self._copy_constructor(other)
        else:
            self.vertices = vertices if vertices else set()
            self.edges = edges if edges else []

    def __str__(self):
        result = "Hypergraph:\n"
        result += "\t Total vertices: %s\n" % (','.join(map(str, self.vertices)))
        result += "\t Edges: \n"
        for edge in self.edges:
            result += "\t\t %s\n" % (str(edge))
        result += '\n'

        return result


    def _copy_constructor(self, other:HyperGraph):
        self.vertices = other.getVertices()
        self.edges = other.getEdges()

    def getVertices(self):
        return self.vertices

    def getEdges(self):
        return self.edges

    def addVertex(self, vertex:Vertex, edge:HyperEdge=None):
        if edge:
            self.edges[self.edges.index(edge)].addVertex(vertex)
        self.vertices.add(vertex)

    def addVertices(self, vertices:set):
        self.vertices |= vertices

    def addEdge(self, edge:HyperEdge):
        self.vertices |= edge.getVertices()
        self.edges.append(edge)

    def addEdges(self, edges):
        for edge in edges:
            self.addEdge(edge)

    def loadJson(self, file):
        hg_dict = json.loads(file.read())
        if 'edges' in hg_dict:
            for edge_dict in hg_dict['edges']:
                vertices = []
                for vertex_dict in edge_dict['vertices']:
                    vertex = Vertex(vertex_dict['id'])
                    # TODO проверять на повторяющиеся вершины
                    vertices.append(vertex)
                edge = HyperEdge(*vertices)
                self.addEdge(edge)
                self.addVertices(set(vertices))
        
        if 'vertices' in hg_dict:
            for vertex_dict in hg_dict['vertices']:
                vertex = Vertex(vertex_dict['id'])
                self.addVertex(vertex)

    def saveJson(self, file_path:Path):
        result = {}

        if self.edges:
            result['edges'] = []

        not_isolated_vertices = set()
        for edge in self.edges:
            vertices_list = []
            for vertex in edge.getVertices():
                not_isolated_vertices.add(vertex)
                vertices_list.append({'id': vertex.getId()})
            result['edges'].append({'vertices': vertices_list})

        isolated_vertices = self.vertices - not_isolated_vertices
        if isolated_vertices:
            result['vertices'] = [{'id': v.getId()} for v in isolated_vertices]

        #file_path.open("w")
        file_path.write_text(json.dumps(result, indent=4))
        #file_path.close()
            

    def isConnected(self):
        # TODO
        return True

    def isSContractable(self, with_linear_condition = False):
        """
            using simple algorithm
        """
        # TODO
        if not self.isConnected():
            return False
        
        edges = self.edges
        vertices = self.vertices
        delete_stack = []           # deleted edges would be placed there (index_of_edge, complex_vertex)
        edge_to_start_with = 0

        EdgeDeletion = namedtuple('EdgeDeletion', ['index', 'new_vertex', 'first_vertex', 'second_vertex', 'first_indices', 'second_indices'])

        while len(vertices) > 1:
            edge_deleted = False
            for i, edge in enumerate(edges[edge_to_start_with:]):      # search edge to delete
                if edge.getDegree() == 2:
                    vertices_to_contract = edge.getVertices()
                    first_vertex_to_contract, second_vertex_to_contract = tuple(vertices_to_contract)
                    new_vertex = first_vertex_to_contract + second_vertex_to_contract
                    first_indices = []
                    second_indices = []

                    for j, reducing_edge in enumerate(edges):
                        if edge is reducing_edge:
                            continue

                        reducing_edge_vertices = reducing_edge.getVertices()
                        if not reducing_edge_vertices.isdisjoint(vertices_to_contract):
                            common_vertices = reducing_edge_vertices & vertices_to_contract
                            if len(common_vertices) == 1:
                                common_vertex = common_vertices.pop()
                                if common_vertex is first_vertex_to_contract:
                                    first_indices.append(j)
                                elif common_vertex is second_vertex_to_contract:
                                    second_indices.append(j)
                                edges[j].deleteVertex(common_vertex)
                                edges[j].addVertex(new_vertex)
                            else:
                                first_indices.append(j)
                                second_indices.append(j)
                                edges[j].deleteVertex(common_vertices.pop())
                                edges[j].deleteVertex(common_vertices.pop())
                                edges[j].addVertex(new_vertex)

                    edges.remove(edge)
                    vertices -= {first_vertex_to_contract, second_vertex_to_contract}
                    vertices.add(new_vertex)
                    # print(HyperGraph(vertices=vertices, edges=edges))
                    delete_stack.append(
                        EdgeDeletion(
                            i + edge_to_start_with,
                            new_vertex,
                            first_vertex_to_contract,
                            second_vertex_to_contract,
                            first_indices,
                            second_indices
                        )
                    )
                    edge_deleted = True
                    break
            
            edge_to_start_with = 0
            if not edge_deleted and delete_stack:   # rollback
                while True:     # edge is not last in the edges list
                    if not delete_stack:
                        return False

                    last_deletion = delete_stack.pop()
                    # restore ComplexVertices in all edges
                    edges.insert(last_deletion.index, HyperEdge(*[last_deletion.first_vertex, last_deletion.second_vertex]))
                    for i in last_deletion.first_indices:
                        edges[i].replaceVertex(last_deletion.new_vertex, last_deletion.first_vertex)
                    for i in last_deletion.second_indices:
                        if last_deletion.new_vertex in edges[i].getVertices():
                            edges[i].replaceVertex(last_deletion.new_vertex, last_deletion.second_vertex)
                        else:
                            edges[i].addVertex(last_deletion.second_vertex)
                    edge_to_start_with = last_deletion[0] + 1
                    vertices -= {last_deletion.new_vertex}
                    vertices |= {last_deletion.first_vertex, last_deletion.second_vertex}
                    # print(HyperGraph(vertices=vertices, edges=edges))
                    if edge_to_start_with < len(edges):
                        break

        return True
