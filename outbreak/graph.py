"""Unit 2: weighted, undirected contact graph (adjacency list)."""
import heapq
import math
from collections import deque
from typing import List, NamedTuple, Tuple

INF = math.inf
RATE = 0.35    # per effective contact hour (model assumption)
MIN_P = 1e-6   # floor so -ln(p) never becomes infinite


class Edge(NamedTuple):
    to: int
    duration: float   # hours of contact, > 0
    proximity: float  # closeness in (0, 1]; 1 = shared room
    p: float          # derived transmission probability in (0, 1]


class PathResult(NamedTuple):
    dist: List[float]   # -ln(path probability); inf if unreachable
    parent: List[int]   # previous node on the best path; -1 for the source/unreachable


def transmission_probability(duration: float, proximity: float) -> float:
    """The ONE place where p is derived.  MODEL ASSUMPTION (not validated epidemiology):

        p = 1 - exp(-RATE * duration * proximity)

    "Exposure dose" = duration * proximity (hours of effective contact). If
    infectious events arrive at a constant rate per dose unit, the chance of at
    least one event is 1 - exp(-rate * dose): ~0 for no contact, -> 1 for long
    close contact, smooth in between. p is clamped to [MIN_P, 1] so it stays in
    (0, 1]; that guarantees -ln(p) is finite and >= 0, which Dijkstra needs. O(1).
    """
    p = 1.0 - math.exp(-RATE * duration * proximity)
    return min(1.0, max(MIN_P, p))


class Graph:
    def __init__(self, num_nodes: int) -> None:
        self.adj: List[List[Edge]] = [[] for _ in range(num_nodes)]
        self.edge_count = 0

    def __len__(self) -> int:
        return len(self.adj)

    def add_edge(self, u: int, v: int, duration: float, proximity: float) -> None:
        """Store an undirected contact as two directed edges."""
        p = transmission_probability(duration, proximity)
        self.adj[u].append(Edge(v, duration, proximity, p))
        self.adj[v].append(Edge(u, duration, proximity, p))
        self.edge_count += 1

    def bfs_levels(self, source: int) -> List[int]:
        """Hops from source to every node (-1 if unreachable): the "exposure level".

        Level 1 = direct contacts, level 2 = contacts of contacts, ...
        Complexity O(V + E). BFS uses a FIFO queue, so nodes leave the queue in
        non-decreasing hop distance; the first time a node is seen is via a
        fewest-hops path.
        """
        level = [-1] * len(self.adj)
        level[source] = 0
        q = deque([source])
        while q:
            u = q.popleft()
            for e in self.adj[u]:
                if level[e.to] == -1:
                    level[e.to] = level[u] + 1
                    q.append(e.to)
        return level

    def find_clusters(self) -> List[int]:
        """Connected components by DFS; returns a label 0..k-1 per node.

        Complexity O(V + E). A DFS from an unlabelled node reaches exactly the
        nodes connected to it, so every outer-loop start begins a new component.
        An explicit stack (not recursion) keeps 100000-node graphs safe.
        """
        label = [-1] * len(self.adj)
        next_label = 0
        for start in range(len(self.adj)):
            if label[start] != -1:
                continue
            label[start] = next_label
            stack = [start]
            while stack:
                u = stack.pop()
                for e in self.adj[u]:
                    if label[e.to] == -1:
                        label[e.to] = next_label
                        stack.append(e.to)
            next_label += 1
        return label

    def likely_path(self, source: int) -> PathResult:
        """Most likely transmission path from source to every node (Dijkstra).

        Complexity O((V + E) log V) with a binary heap.
        Why it works: a path's probability is the PRODUCT of its edge
        probabilities. Taking -ln turns products into sums,
        -ln(p1*p2*...) = sum(-ln pi), and maximising the product = minimising the
        sum. Every weight -ln(p) >= 0 because p <= 1, and Dijkstra is correct
        exactly when weights are non-negative. So dist[v] = -ln(best path
        probability) and exp(-dist[v]) is that probability.
        heapq (a priority queue) is allowed here; stale entries are skipped.
        """
        dist = [INF] * len(self.adj)
        parent = [-1] * len(self.adj)
        dist[source] = 0.0
        pq: List[Tuple[float, int]] = [(0.0, source)]
        while pq:
            d, u = heapq.heappop(pq)
            if d > dist[u]:
                continue  # outdated entry
            for e in self.adj[u]:
                nd = d - math.log(e.p)  # -ln(p) >= 0
                if nd < dist[e.to]:
                    dist[e.to] = nd
                    parent[e.to] = u
                    heapq.heappush(pq, (nd, e.to))
        return PathResult(dist, parent)

    @staticmethod
    def reconstruct_path(r: PathResult, source: int, target: int) -> List[int]:
        """Node list source..target from the parent array (empty if unreachable).

        O(path length). Parents form a tree rooted at the source, so walking
        parents from the target reaches the source; reverse for the order.
        """
        if r.dist[target] == INF:
            return []
        path, v = [], target
        while v != -1:
            path.append(v)
            v = r.parent[v]
        path.reverse()
        return path if path[0] == source else []

    def hop_path(self, source: int, target: int) -> List[int]:
        """Baseline path with the fewest edges, ignoring probabilities. O(V + E).

        BFS with parent pointers; stops once the target is reached because BFS
        finds fewest-hops paths first.
        """
        parent = {source: -1}
        q = deque([source])
        while q and target not in parent:
            u = q.popleft()
            for e in self.adj[u]:
                if e.to not in parent:
                    parent[e.to] = u
                    q.append(e.to)
        if target not in parent:
            return []
        path, v = [], target
        while v != -1:
            path.append(v)
            v = parent[v]
        path.reverse()
        return path

    def edge_probability(self, u: int, v: int) -> float:
        """Probability of the best edge between u and v (0 if not adjacent). O(degree(u))."""
        return max((e.p for e in self.adj[u] if e.to == v), default=0.0)

    def path_probability(self, path: List[int]) -> float:
        """Probability that infection crosses every hop of a path (hops independent,
        so probabilities multiply). Empty path (unreachable) = 0; a single node = 1."""
        if not path:
            return 0.0
        prob = 1.0
        for a, b in zip(path, path[1:]):
            prob *= self.edge_probability(a, b)
        return prob
