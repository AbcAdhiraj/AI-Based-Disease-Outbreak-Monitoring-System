"""Minimal test harness, no framework. Run: python3 tests/test_all.py (exit code 1 on failure)."""
import math
import os
import random
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from outbreak.allocation import (brute_force_allocate, discretise_series, dp_allocate,
                                 greedy_allocate, lcs_length, lcs_similarity)
from outbreak.avl_tree import AvlTree
from outbreak.bst_baseline import BstBaseline
from outbreak.data_gen import (case_series_for_wards, generate_contact_graph, generate_patients,
                               random_allocation_instance)
from outbreak.graph import Graph, transmission_probability
from outbreak.max_heap import MaxHeap
from outbreak.patient import Patient
from outbreak.risk import build_risk_heap, node_risk, ward_risk

checks = failed = 0


def check(cond, what=""):
    """Assert-style check that records the result and keeps going."""
    global checks, failed
    checks += 1
    if not cond:
        failed += 1
        line = sys._getframe(1).f_lineno
        print(f"  FAIL line {line} {what}")


def near(a, b):
    return abs(a - b) < 1e-9


def pt(i):
    return Patient(i, 30, i % 5, 1 + i % 5)


def test_avl_sorted_input():
    t = AvlTree()
    for i in range(1, 1001):
        t.insert(pt(i))
    check(t.validate())
    check(len(t) == 1000)
    check(t.height() <= 14, "height bound 1.44*log2(1001)")
    b = BstBaseline()
    for i in range(1, 1001):
        b.insert(pt(i))
    check(b.height() == 1000, "baseline degenerates into a list")


def test_avl_rotations():
    for order in ([3, 2, 1], [1, 2, 3], [3, 1, 2], [1, 3, 2]):  # LL, RR, LR, RL
        t = AvlTree()
        for i in order:
            t.insert(pt(i))
        check(t.root_id() == 2 and t.height() == 2 and t.validate(), str(order))


def test_avl_random_ops():
    rng = random.Random(7)
    t, ref = AvlTree(), set()
    for step in range(4000):
        k = rng.randrange(600)
        if rng.random() < 0.67:
            check(t.insert(pt(k)) == (k not in ref))
            ref.add(k)
        else:
            check(t.remove(k) == (k in ref))
            ref.discard(k)
        if step % 200 == 0:
            check(t.validate())
    check(t.validate() and len(t) == len(ref))
    check([p.id for p in t.inorder()] == sorted(ref))


def test_avl_search_and_range():
    t, b = AvlTree(), BstBaseline()
    for i in range(0, 100, 2):
        t.insert(pt(i))
        b.insert(pt(i))
    check(t.search(40).id == 40)
    check(t.search(41) is None and t.search(-5) is None)
    r = t.range(11, 25)  # 12,14,...,24
    check([p.id for p in r] == [12, 14, 16, 18, 20, 22, 24])
    check(t.range(200, 300) == [] and len(t.range(0, 98)) == 50)
    check([p.id for p in b.range(11, 25)] == [p.id for p in r])
    check(b.validate() and b.remove(40) and b.search(40) is None and b.validate())
    check(not b.remove(41))
    for k in (0, 50, 98):  # remove root-ish / two-children cases and re-validate
        check(b.remove(k) and b.validate())


def test_heap():
    rng = random.Random(3)
    h = MaxHeap()
    for i in range(2000):
        h.push(i, rng.randrange(1000) / 7.0)
    check(len(h) == 2000)
    prev, ordered = math.inf, True
    while len(h):
        top = h.peek().score
        x = h.pop()
        ordered = ordered and x.score == top and x.score <= prev
        prev = x.score
    check(ordered)
    h.push(1, 0.5)
    h.push(2, 0.9)
    check(h.peek().id == 2 and len(h) == 2)


def hand_graph():
    g = Graph(8)  # 0-1-2-3 chain, 1-4 branch; 5-6 separate pair; 7 isolated
    for u, v in ((0, 1), (1, 2), (2, 3), (1, 4), (5, 6)):
        g.add_edge(u, v, 2, 1)
    return g


def test_graph_probability():
    for d in (0.001, 0.5, 3.0, 50.0):
        for pr in (0.01, 0.5, 1.0):
            check(0.0 < transmission_probability(d, pr) <= 1.0)
    check(transmission_probability(5, 1) > transmission_probability(1, 1))
    check(transmission_probability(2, 1) > transmission_probability(2, 0.2))


def test_graph_bfs_clusters():
    g = hand_graph()
    check(g.bfs_levels(0) == [0, 1, 2, 3, 2, -1, -1, -1])
    c = g.find_clusters()
    check(len({c[0], c[1], c[2], c[3], c[4]}) == 1 and c[5] == c[6])
    check(len({c[0], c[5], c[7]}) == 3 and max(c) + 1 == 3)


def brute(g, u, target, seen, cost, best):
    """Enumerate every simple path u->target; best[0] keeps the smallest sum of -ln(p)."""
    if u == target:
        best[0] = min(best[0], cost)
        return
    seen.add(u)
    for e in g.adj[u]:
        if e.to not in seen:
            brute(g, e.to, target, seen, cost - math.log(e.p), best)
    seen.discard(u)


def test_dijkstra_vs_bruteforce():
    rng = random.Random(11)
    for _ in range(300):
        n = rng.randint(2, 8)
        g = Graph(n)
        for u in range(n):
            for v in range(u + 1, n):
                if rng.random() < 0.45:
                    g.add_edge(u, v, rng.uniform(0.1, 5.0), rng.uniform(0.1, 1.0))
        src = rng.randrange(n)
        r = g.likely_path(src)
        for t in range(n):
            best = [math.inf]
            brute(g, src, t, set(), 0.0, best)
            check((math.isinf(best[0]) and math.isinf(r.dist[t])) or near(best[0], r.dist[t]))
            path = Graph.reconstruct_path(r, src, t)
            if math.isinf(best[0]):
                check(path == [] and g.hop_path(src, t) == [])
            else:
                check(near(g.path_probability(path), math.exp(-best[0])))
                check(len(g.hop_path(src, t)) <= len(path), "hop path has fewest nodes")


def test_likely_vs_hop_differ():
    g = Graph(3)  # weak direct edge 0-2; strong two-hop route via 1
    g.add_edge(0, 2, 0.2, 0.1)
    g.add_edge(0, 1, 6.0, 1.0)
    g.add_edge(1, 2, 6.0, 1.0)
    hop = g.hop_path(0, 2)
    likely = Graph.reconstruct_path(g.likely_path(0), 0, 2)
    check(len(hop) == 2 and len(likely) == 3)
    check(g.path_probability(likely) > g.path_probability(hop))


def test_risk():
    g = Graph(4)  # 0-1-2 chain, 3 isolated
    g.add_edge(0, 1, 2, 1)
    g.add_edge(1, 2, 1, 0.5)
    r = node_risk(g, [0])
    p01, p12 = g.edge_probability(0, 1), g.edge_probability(1, 2)
    check(near(r[0], 1.0) and near(r[1], p01) and near(r[2], p01 * p12) and near(r[3], 0.0))
    r2 = node_risk(g, [0, 2])
    check(near(r2[1], 1 - (1 - p01) * (1 - p12)))
    pts = [Patient(0, 20, 0, 1), Patient(1, 20, 0, 1), Patient(2, 20, 1, 1), Patient(3, 20, 1, 1)]
    check(near(ward_risk(pts, r, 2)[0], (1 + p01) / 2))
    h = build_risk_heap(r, [True, False, False, False])
    check(len(h) == 3 and h.peek().id == 1)


def test_dp_vs_bruteforce():
    for seed in range(300):
        wards, opts, budget = 1 + seed % 5, 2 + seed % 3, 3 + seed % 13
        w = random_allocation_instance(wards, opts, seed)
        dp, bf = dp_allocate(w, budget), brute_force_allocate(w, budget)
        check(dp.feasible and bf.feasible and near(dp.total_value, bf.total_value))
        check(dp.total_cost <= budget)
        value = sum(w[i][dp.choice[i]].value for i in range(wards))
        cost = sum(w[i][dp.choice[i]].cost for i in range(wards))
        check(near(value, dp.total_value) and cost == dp.total_cost, "backtracking is consistent")


def test_greedy_strictly_worse():
    from outbreak.allocation import Option as O
    w = [[O(0, 0), O(1, 3)],    # ratio 3: greedy grabs it first
         [O(0, 0), O(5, 10)]]   # ratio 2: no longer fits afterwards
    dp, gr = dp_allocate(w, 5), greedy_allocate(w, 5)
    check(near(dp.total_value, 10.0) and near(gr.total_value, 3.0))
    check(dp.total_value > gr.total_value and dp.choice == [0, 1])
    for seed in range(100):  # greedy is never better than DP
        r = random_allocation_instance(6, 4, seed)
        check(dp_allocate(r, 15).total_value + 1e-9 >= greedy_allocate(r, 15).total_value)


def test_infeasible():
    from outbreak.allocation import Option as O
    w = [[O(3, 1.0)], [O(4, 2.0)]]
    check(not dp_allocate(w, 5).feasible)
    check(dp_allocate(w, 7).feasible and near(dp_allocate(w, 7).total_value, 3.0))


def test_lcs():
    check(lcs_length("ABCBDAB", "BDCABA") == 4)
    check(lcs_length("AGGTAB", "GXTXAYB") == 4)
    check(lcs_length("", "ABC") == 0 and lcs_length("ABC", "DEF") == 0)
    check(lcs_length("RRFD", "RRFD") == 4 and near(lcs_similarity("RRFD", "RRFD"), 1.0))
    check(near(lcs_similarity("ABCBDAB", "BDCABA"), 4 / 7))
    check(near(lcs_similarity("", ""), 1.0) and near(lcs_similarity("RRR", "DDD"), 0.0))
    check(discretise_series([10, 20, 20.5, 10]) == "RFD" and discretise_series([5]) == "")


def test_data_gen():
    g = generate_contact_graph(1000, 6.0, 5)
    g2 = generate_contact_graph(1000, 6.0, 5)
    check(g.edge_count == 3000 and g2.edge_count == 3000 and g.adj[10] == g2.adj[10])
    p = generate_patients(50, 4, 1)
    check(len(p) == 50 and p[49].id == 49 and all(0 <= x.ward < 4 for x in p))
    series, real = case_series_for_wards("no_such_file.csv", 3, 10, 1)
    check(not real and len(series) == 3 and len(series[0]) == 10)
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "jhu.csv")
        with open(path, "w") as f:
            f.write("Province/State,Country/Region,Lat,Long,1/1/20,1/2/20,1/3/20\n")
            f.write(",Afghanistan,33,65,0,2,5\n")
            f.write('"X, Y",Albania,41,20,1,1,4\n')
        series, real = case_series_for_wards(path, 2, 2, 1)
        check(real and series == [[2.0, 3.0], [0.0, 3.0]])


TESTS = [
    ("AVL: sorted 1..1000 stays balanced", test_avl_sorted_input),
    ("AVL: four rotations", test_avl_rotations),
    ("AVL: random insert/delete keep validate()", test_avl_random_ops),
    ("AVL: search and range query", test_avl_search_and_range),
    ("Heap: pops in non-increasing order", test_heap),
    ("Graph: transmission probability in (0,1]", test_graph_probability),
    ("Graph: BFS levels and clusters", test_graph_bfs_clusters),
    ("Graph: Dijkstra == brute force (<= 8 nodes)", test_dijkstra_vs_bruteforce),
    ("Graph: likely path differs from fewest-hops path", test_likely_vs_hop_differ),
    ("Risk: formula, ward risk, heap", test_risk),
    ("Allocation: DP == brute force", test_dp_vs_bruteforce),
    ("Allocation: greedy strictly worse than DP", test_greedy_strictly_worse),
    ("Allocation: infeasible budget", test_infeasible),
    ("LCS: known answers and discretiser", test_lcs),
    ("Data generation and CSV loader", test_data_gen),
]

if __name__ == "__main__":
    for name, fn in TESTS:
        before = failed
        fn()
        print(f"[{'PASS' if failed == before else 'FAIL'}] {name}")
    print(f"\n{checks} checks, {failed} failed")
    sys.exit(1 if failed else 0)
