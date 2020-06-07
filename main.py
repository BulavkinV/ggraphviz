import cProfile
from pathlib import Path
import logging

from Hypergraph import HyperGraph
from HyperEdge import HyperEdge
from Vertex import Vertex

def loadSampleHyperGraph():
    h = HyperGraph()
    # vertices = [Vertex(i) for i in range(1, 9)]
    # h.addVertices(vertices)
    edges = [
        (1, 2),
        (2, 8),
        (2, 7, 4),
        (4, 8),
        (8, 6),
        (8, 5, 6),
        (6, 3)
    ]
    edges = [HyperEdge(*[Vertex(x) for x in vertices]) for vertices in edges]
    h.addEdges(edges)
    # h.addVertex(Vertex('ok'))
    return h

graph_directory = Path('Graphs')
# h = HyperGraph()
# h.loadJson(open(graph_directory / 'SampleOverbasedGraph.json', 'r'))

# print(h)
# print(h.isSContractable())

import sys

from PyQt5.Qt import QApplication
from Graphics.MainWindow import MainWindow
from Graphics.CanvasHyperGraph import CanvasHyperGraph

from Hypergraph import HyperGraph

if __name__ == '__main__':

    logging.basicConfig(level=logging.DEBUG)
    
    app = QApplication(sys.argv)
    h = HyperGraph()
    # h.addVertex(Vertex("Sample Vertex"))
    # h.loadJson(open(graph_directory / 'SampleGraph1.json', 'r'))

    ch = CanvasHyperGraph(h)
    w = MainWindow(ch)
    w.show()
    sys.exit(app.exec_())