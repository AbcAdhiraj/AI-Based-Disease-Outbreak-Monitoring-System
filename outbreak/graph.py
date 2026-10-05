"""Unit 2: the contact graph (undirected, weighted, stored as an adjacency list).

Each patient is a node. An edge between two patients means they were in contact.
The adjacency list is a list where position u holds the list of u's edges.
"""
import heapq
import math
from collections import deque   # a fast queue for BFS

INF = math.inf   # "infinity" = not reachable (yet)

# Model constants (assumptions, not real epidemiology).
RATE = 0.35      # infection chance per "effective contact hour"
MIN_P = 1e-6     # smallest allowed p, so that -ln(p) never becomes infinite


class Edge:
    """One direction of a contact: from some node u TO node `to`."""

    def __init__(self, to, duration, proximity, p):
        self.to = to                # the patient at the other end
        self.duration = duration    # hours of contact (> 0)
        self.proximity = proximity  # closeness in (0, 1]; 1 = same room
        self.p = p                  # transmission probability in (0, 1]


class PathResult:
    """What Dijkstra returns: for every node, its distance and its previous node."""

    def __init__(self, dist, parent):
        self.dist = dist        # dist[v] = -ln(probability of the best path to v)
        self.parent = parent    # parent[v] = the node before v on that path (-1 = none)


def transmission_probability(duration, proximity):
    """The ONE place where the probability p of an edge is calculated.

    MODEL ASSUMPTION (not validated epidemiology):

        p = 1 - exp(-RATE * duration * proximity)

    Reasoning: "duration * proximity" is the effective contact time. Longer and
    closer contact should give a higher chance. 1 - exp(-x) is a standard
    formula for "chance that at least one infection event happens"; it is
    0 when x = 0, grows with x, and never goes above 1. We clamp p to
    [MIN_P, 1] so it is always in (0, 1] (this keeps -ln(p) finite and >= 0).
    """
    p = 1.0 - math.exp(-RATE * duration * proximity)
    if p < MIN_P:
        p = MIN_P
    if p > 1.0:
        p = 1.0
    return p


class Graph:
    def __init__(self, num_nodes):
        # One empty edge list per node.
        self.adj = []
        for i in range(num_nodes):
            self.adj.append([])
        self.edge_count = 0

    def __len__(self):
        return len(self.adj)

    def add_edge(self, u, v, duration, proximity):
        """Add a contact between u and v. Stored twice because it is undirected."""
        p = transmission_probability(duration, proximity)
        self.adj[u].append(Edge(v, duration, proximity, p))   # u -> v
        self.adj[v].append(Edge(u, duration, proximity, p))   # v -> u
        self.edge_count += 1

    def bfs_levels(self, source):
        """Number of hops from source to every node; -1 if unreachable.

        This is the "exposure level": level 1 = direct contacts, level 2 =
        contacts of contacts, and so on.
        Time: O(V + E) - every node and edge is looked at once.
        Why it works: BFS uses a FIFO queue, so nodes are processed in order of
        distance. The first time we reach a node is by the fewest hops.
        """
        level = [-1] * len(self.adj)    # -1 means "not visited yet"
        level[source] = 0
        queue = deque()
        queue.append(source)
        while len(queue) > 0:
            u = queue.popleft()                 # take the oldest node in the queue
            for edge in self.adj[u]:            # look at each neighbour of u
                if level[edge.to] == -1:        # first visit
                    level[edge.to] = level[u] + 1
                    queue.append(edge.to)
        return level

    def find_clusters(self):
        """Split the graph into clusters (connected components) using DFS.

        Returns a list where label[v] is the cluster number (0, 1, 2, ...) of node v.
        Time: O(V + E).
        Why it works: a DFS started at a node reaches exactly the nodes connected
        to it, so every time we start a new DFS we have found a new cluster.
        We use our own stack (a list) instead of recursion so very big graphs
        cannot crash Python.
        """
        label = [-1] * len(self.adj)    # -1 means "no cluster yet"
        next_label = 0
        for start in range(len(self.adj)):
            if label[start] != -1:
                continue                # already in a cluster
            label[start] = next_label   # start a new cluster
            stack = [start]
            while len(stack) > 0:
                u = stack.pop()         # take the NEWEST node (that is what makes it DFS)
                for edge in self.adj[u]:
                    if label[edge.to] == -1:
                        label[edge.to] = next_label
                        stack.append(edge.to)
            next_label += 1
        return label

    def likely_path(self, source):
        """Find the MOST LIKELY transmission path from source to every node (Dijkstra).

        Time: O((V + E) log V) when a heap is used.
        The probability of a path is the PRODUCT of its edge probabilities, but
        Dijkstra adds weights. The trick: -ln(a * b) = -ln(a) + -ln(b), so if
        every edge gets weight -ln(p) then
          * adding weights  = multiplying probabilities, and
          * the SMALLEST total weight = the LARGEST probability.
        Since p <= 1, every weight -ln(p) is >= 0, and Dijkstra needs
        non-negative weights. At the end exp(-dist[v]) is the best probability.
        """
        dist = [INF] * len(self.adj)    # best known distance to each node
        parent = [-1] * len(self.adj)   # previous node on the best known path
        dist[source] = 0.0
        heap = [(0.0, source)]          # (distance, node); heapq keeps the smallest on top
        while len(heap) > 0:
            d, u = heapq.heappop(heap)  # the unfinished node closest to the source
            if d > dist[u]:
                continue                # old entry: we already found a better path to u
            for edge in self.adj[u]:
                new_dist = d - math.log(edge.p)     # -ln(p) is the edge weight
                if new_dist < dist[edge.to]:        # found a better path to the neighbour
                    dist[edge.to] = new_dist
                    parent[edge.to] = u
                    heapq.heappush(heap, (new_dist, edge.to))
        return PathResult(dist, parent)

    def reconstruct_path(self, result, source, target):
        """Turn Dijkstra's parent list into a list of nodes [source, ..., target].

        Returns [] if the target cannot be reached. Time: O(length of path).
        We start at the target and follow the parents back to the source, so
        the list comes out backwards and we reverse it at the end.
        """
        if result.dist[target] == INF:
            return []
        path = []
        node = target
        while node != -1:
            path.append(node)
            node = result.parent[node]
        path.reverse()
        return path

    def hop_path(self, source, target):
        """The path with the FEWEST hops, ignoring probabilities. Time: O(V + E).

        It is a BFS that remembers where each node came from. BFS reaches every
        node by the fewest hops, so we can stop as soon as the target is found.
        """
        parent = [-1] * len(self.adj)
        seen = [False] * len(self.adj)
        seen[source] = True
        queue = deque()
        queue.append(source)
        while len(queue) > 0 and not seen[target]:
            u = queue.popleft()
            for edge in self.adj[u]:
                if not seen[edge.to]:
                    seen[edge.to] = True
                    parent[edge.to] = u
                    queue.append(edge.to)
        if not seen[target]:
            return []                    # target is in another cluster
        path = []
        node = target
        while node != -1:                # walk back from the target to the source
            path.append(node)
            node = parent[node]
        path.reverse()
        return path

    def edge_probability(self, u, v):
        """Probability of the edge between u and v (0 if they are not neighbours)."""
        best = 0.0
        for edge in self.adj[u]:
            if edge.to == v and edge.p > best:
                best = edge.p
        return best

    def path_probability(self, path):
        """Probability that infection travels along a whole path.

        Each step is assumed independent, so we multiply the edge probabilities.
        An empty path (no route) gives 0. A path of one node gives 1.
        """
        if len(path) == 0:
            return 0.0
        probability = 1.0
        for i in range(1, len(path)):
            probability = probability * self.edge_probability(path[i - 1], path[i])
        return probability
