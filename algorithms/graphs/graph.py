"""
Graphs Module
"""
import queue
import sys
from datastructures.heap import MutablePriorityQueue


# Colors used by the search algorithms
WHITE = 0
BLACK = 1
GRAY = 2


class Vertex:
    def __init__(self, key):
        self.id = key
        # map from a neighbour vertex to the weight of the edge
        self.connected_to = {}
        # maps a distance from a source vertex to this vertex
        # ex: dist[neighbour_1] = 4 => dist(neighbour_1, self) = 4
        self.dist = {}
        # color of this vertex for search algorithms, initialized as WHITE
        self.color = WHITE
        # predecessor, initialized as None
        self.predecessor = None

    def __str__(self):
        return str(self.id) + " connected to: " + str([x.id for x in self.connected_to])

    def add_neighbour(self, neighbour, weight):
        """
        Adds the neighbour to the connected_to map with the corresponding weight.
        :param neighbour: the neighbour to be added
        :param weight: the weight of the edge
        """
        self.connected_to[neighbour] = weight

    def get_connections(self):
        """
        :return: all neighbours of this vertex
        """
        return self.connected_to.keys()

    def get_id(self):
        """
        :return: the id of this vertex
        """
        return self.id

    def get_weight(self, neighbour):
        """
        Returns the weight of the edge between this vertex and neighbour
        :param neighbour: the neighbour
        :return: the weight of the edge
        """
        return self.connected_to[neighbour]


class Graph:
    def __init__(self, directed=True):
        self.vertices = {}
        self.num_vertices = 0
        self.directed = directed

    def __contains__(self, item):
        return item in self.vertices

    def __iter__(self):
        return iter(self.vertices.values())

    ############################################
    # Basic commands and queries for the Graph #
    ############################################

    def get_vertex(self, key):
        """
        :param key: key of the vertex
        :return: the Vertex object given the key, or raises KeyError
        """
        if key in self.vertices:
            return self.vertices[key]
        else:
            raise KeyError("No Vertex with that key.")

    def get_vertices(self):
        """
        :return: the keys of the vertices in the graph
        """
        return self.vertices.keys()

    def get_edges(self):
        """
        :return: a list of edges in the graph
        """
        edges = []
        for v in self:
            for u in v.get_connections():
                edges.append((v, u, v.get_weight(u)))
        return edges

    def add_vertex(self, key):
        """
        Adds a vertex with the specified key to the graph.
        :param key: the key of the vertex
        """
        self.num_vertices += 1
        new_vertex = Vertex(key)
        self.vertices[key] = new_vertex

    def add_edges(self, edges: list):
        """
        Calls self.add_edges for all edges in the edges list.
        :param edges: list of edges
        """
        for edge in edges:
            self.add_edge(edge)

    def add_edge(self, *edge):
        """
        Adds an edge given a tuple of the form:
         - (vertex_1, vertex_2) for non-weighted graphs
         - (vertex_1, vertex_2, weight) for weighted graphs
        where vertex_1 and vertex_2 are keys, not Vertex objects.
        :param edge: the edge to be added
        """
        vertex_1, vertex_2, *cost = edge
        if vertex_1 not in self.vertices:
            self.add_vertex(vertex_1)
        if vertex_2 not in self.vertices:
            self.add_vertex(vertex_2)
        if len(cost) == 0:
            self.vertices[vertex_1].add_neighbour(self.vertices[vertex_2], 0)
            if not self.directed:
                self.vertices[vertex_2].add_neighbour(self.vertices[vertex_1], 0)
        else:
            self.vertices[vertex_1].add_neighbour(self.vertices[vertex_2], cost[0])
            if not self.directed:
                self.vertices[vertex_2].add_neighbour(self.vertices[vertex_1], cost[0])

    ###################################
    # Search algorithms for the graph #
    ###################################

    def connected(self, key_1, key_2):
        """
        :param key_1: vertex with key_1
        :param key_2: vertex with key_2
        :return: true if vertex 1 is connected to vertex 2, false otherwise
        """
        neighbours = self.vertices[key_1].get_connections()
        for neighbour in neighbours:
            if key_2 == neighbour.get_id():
                return True
        return False

    def print_path(self, key_source, key_destination):
        """
        Prints the path from source to destination if it exists.
        Assumes that the predecessor have been computed.
        :param key_source: key of source vertex
        :param key_destination: key of destination vertex
        """
        source = self.get_vertex(key_source)
        destination = self.get_vertex(key_destination)
        self._print_path_util(source, destination)

    def _print_path_util(self, source, destination):
        """
        Main print path algorithm.
        :param source: source vertex
        :param destination: destination vertex
        """
        if source is destination:
            print(source.get_id(), end=" ")
        elif destination.predecessor is None:
            print("No path from {} to {} exists!".format(source.get_id(), destination.get_id()))
        else:
            self._print_path_util(source, destination.predecessor)
            print(destination.get_id(), end=" ")

    def bfs(self, source_key):
        """
        Runs the BFS algorithm from source_key and computes
        the shortest number of edges from the source to all
        other vertices and predecessor of every vertex.
        :param source_key: the key of the source vertex
        """
        source: Vertex = self.get_vertex(source_key)
        for u in self:
            if u is not source:
                u.color = WHITE
                u.predecessor = None
                # initialize the distance from the source
                u.dist[source] = sys.maxsize
        source.color = GRAY
        source.dist[source] = 0
        source.predecessor = None
        # initialize queue with max size number of vertices
        q = queue.Queue(self.num_vertices)
        q.put(source)
        while not q.empty():
            u: Vertex = q.get()
            for v in u.get_connections():
                if v.color is WHITE:
                    v.color = GRAY
                    v.dist[source] = u.dist[source] + 1
                    v.predecessor = u
                    q.put(v)
            u.color = BLACK

    def dfs(self):
        """
        Runs Depth First Search on this graph.
        """
        for u in self:
            u.color = WHITE
            u.predecessor = None
        for u in self:
            if u.color is WHITE:
                self.dfs_visit(u)

    def dfs_visit(self, u: Vertex):
        """
        Explores a Vertex u. Called by dfs
        :param u: the explored vertex
        """
        print(u.get_id(), end=" ")
        u.color = GRAY
        for v in u.get_connections():
            if v.color is WHITE:
                v.predecessor = u
                self.dfs_visit(v)
        u.color = BLACK

    def initialize_single_source(self, source):
        """
        Initialization method used by single source shortest path algorithms.
        :param source: the source vertex
        """
        for v in self:
            v.dist[source] = sys.maxsize
            v.predecessor = None
        source.dist[source] = 0

    @staticmethod
    def relax(source, u, v, weight):
        """
        Performs a relaxation operation for u and v.
        :param source: source of the shortest path algorithm
        :param u: vertex 1
        :param v: vertex 2
        :param weight: weight of the edge between u and v
        """
        if v.dist[source] > u.dist[source] + weight:
            v.dist[source] = u.dist[source] + weight
            v.predecessor = u

    @staticmethod
    def relax_with_priority_update(source, u, v, weight, priority_queue):
        """
        Performs a relaxation operation for u and v.
        Updates the priority queue with a new key for v
        :param source: source of the shortest path algorithm
        :param u: vertex 1
        :param v: vertex 2
        :param weight: weight of the edge between u and v
        :param priority_queue: to be updated
        """
        if v.dist[source] > u.dist[source] + weight:
            v.dist[source] = u.dist[source] + weight
            v.predecessor = u
            priority_queue.add_task(v, v.dist[source])

    def bellman_ford(self, source_key):
        """
        Applies the Bellman-Ford shortest path algorithm from source_key.
        Only works for graphs that do not contain a negative weight cycle.
        If a negative weight cycle is found, the method raises a ValueError.
        :param source_key: the key of the source vertex
        """
        source: Vertex = self.get_vertex(source_key)
        self.initialize_single_source(source)
        for _ in range(self.num_vertices - 1):
            for edge in self.get_edges():
                self.relax(source, edge[0], edge[1], edge[2])
        for edge in self.get_edges():
            if edge[1].dist[source] > edge[0].dist[source] + edge[2]:
                raise ValueError("Negative Weight Cycle Found")

    def dijkstra(self, source_key):
        """
        Applies the Dijkstra shortest path algorithm from source_key.
        Only works for graphs with positive weights.
        :param source_key: the key of the source vertex
        """
        source: Vertex = self.get_vertex(source_key)
        self.initialize_single_source(source)
        priority_queue = MutablePriorityQueue()
        for v_key in self.get_vertices():
            v: Vertex = self.get_vertex(v_key)
            priority_queue.add_task(v, v.dist[source])
        while not priority_queue.empty():
            u: Vertex = priority_queue.pop_task()
            for v in u.get_connections():
                self.relax_with_priority_update(source, u, v, u.get_weight(v), priority_queue)


if __name__ == "__main__":
    g = Graph()
    for i in range(6):
        g.add_vertex(i)
    g.add_edge(0, 1, 5)
    g.add_edge(0, 5, 2)
    g.add_edge(1, 2, 4)
    g.add_edge(2, 3, 9)
    g.add_edge(3, 4, 7)
    g.add_edge(3, 5, 3)
    g.add_edge(4, 0, 1)
    g.add_edge(5, 4, 8)
    g.add_edge(5, 2, 1)
    for g_edge in g.get_edges():
        print("({}, {}) with weight {}".format(g_edge[0].get_id(), g_edge[1].get_id(), g_edge[2]))
    g.bfs(0)
    s = g.get_vertex(0)
    for vertex in g:
        print("Shortest number of edges from 0 to {}: {}".format(vertex.get_id(), vertex.dist[s]))
    g.dijkstra(0)
    s = g.get_vertex(0)
    for vertex in g:
        print("Shortest path from 0 to {}: {}".format(vertex.get_id(), vertex.dist[s]))
