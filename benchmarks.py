"""Benchmarks. Every number printed or saved comes from a real run of this file.

Usage:  python3 benchmarks.py            (saves CSV files into results/)
        python3 benchmarks.py --full     (also times the plain BST at n = 100000)

Each timing is repeated 5 times on the SAME input and the mean (average) is reported.

Note: inserting 100000 SORTED keys into the plain BST takes about 5 billion steps
(O(n^2)), which is many minutes per repeat in Python. So that one measurement is
skipped unless you pass --full. A skipped cell says "skipped"; no numbers are invented.
"""
import os
import random
import sys
import time

from outbreak.allocation import dp_allocate, greedy_allocate
from outbreak.avl_tree import AvlTree
from outbreak.bst_baseline import BstBaseline
from outbreak.data_gen import generate_contact_graph, random_allocation_instance
from outbreak.patient import Patient

REPEATS = 5


def time_it(function, *arguments):
    """Call function(*arguments) REPEATS times.

    Returns (mean time in milliseconds, the result of the last call).
    """
    total_seconds = 0.0
    result = None
    for i in range(REPEATS):
        start = time.perf_counter()               # clock before
        result = function(*arguments)
        total_seconds += time.perf_counter() - start   # add the elapsed time
    return total_seconds / REPEATS * 1000.0, result


def build_avl(patients):
    tree = AvlTree()
    for patient in patients:
        tree.insert(patient)
    return tree


def build_bst(patients):
    tree = BstBaseline()
    for patient in patients:
        tree.insert(patient)
    return tree


def save_csv(folder, filename, lines):
    """Write a list of text lines to folder/filename."""
    with open(os.path.join(folder, filename), "w") as f:
        f.write("\n".join(lines) + "\n")


def bench_trees(folder, run_full):
    print("\n[1] AVL vs plain BST, sorted insertions (mean of %d runs)" % REPEATS)
    print("%-8s%-12s%-12s%-14s%-14s" % ("n", "AVL height", "BST height", "AVL ms", "BST ms"))
    lines = ["n,avl_height,bst_height,avl_ms,bst_ms"]
    for n in [1000, 10000, 100000]:
        # The same list of patients (ids already sorted 0..n-1) goes into both trees.
        patients = []
        for i in range(n):
            patients.append(Patient(i, 40, i % 5, 1 + i % 5))

        avl_ms, avl_tree = time_it(build_avl, patients)
        if n == 100000 and not run_full:
            bst_height = "skipped"
            bst_ms = "skipped"
            bst_ms_text = "skipped"
        else:
            bst_ms, bst_tree = time_it(build_bst, patients)
            bst_height = bst_tree.height()
            bst_ms_text = "%.3f" % bst_ms
        print("%-8d%-12d%-12s%-14.3f%-14s"
              % (n, avl_tree.height(), bst_height, avl_ms, bst_ms_text))
        lines.append("%d,%d,%s,%s,%s" % (n, avl_tree.height(), bst_height, avl_ms, bst_ms))
    save_csv(folder, "bench_tree.csv", lines)


def bench_paths(folder):
    print("\n[2] Dijkstra (most likely) vs BFS (fewest hops), average degree 6")
    print("%-8s%-9s%-13s%-10s%-7s%-8s%-10s%-15s%-12s"
          % ("nodes", "edges", "dijkstra ms", "bfs ms", "pairs", "differ", "differ %",
             "mean p likely", "mean p hops"))
    lines = ["nodes,edges,dijkstra_ms,bfs_ms,pairs,paths_differ,differ_pct,"
             "mean_p_likely,mean_p_hops"]
    for n in [1000, 10000, 100000]:
        graph = generate_contact_graph(n, 6.0, 99)     # the same graph for both methods

        # Runtime: both start at node 0 and compute results for ALL nodes.
        dijkstra_ms, ignore = time_it(graph.likely_path, 0)
        bfs_ms, ignore = time_it(graph.bfs_levels, 0)

        # How often do the two paths differ? Try 20 random sources x 10 random targets.
        rng = random.Random(123)
        pairs = 0
        differ = 0
        sum_p_likely = 0.0
        sum_p_hops = 0.0
        for s in range(20):
            source = rng.randrange(n)
            result = graph.likely_path(source)       # one Dijkstra serves all 10 targets
            for t in range(10):
                target = rng.randrange(n)
                if target == source:
                    continue
                likely = graph.reconstruct_path(result, source, target)
                if len(likely) == 0:
                    continue                         # not connected: nothing to compare
                hops = graph.hop_path(source, target)
                pairs += 1
                if likely != hops:                   # the two lists of nodes are different
                    differ += 1
                sum_p_likely += graph.path_probability(likely)
                sum_p_hops += graph.path_probability(hops)

        if pairs > 0:
            differ_pct = 100.0 * differ / pairs
            mean_likely = sum_p_likely / pairs
            mean_hops = sum_p_hops / pairs
        else:
            differ_pct = mean_likely = mean_hops = 0.0
        print("%-8d%-9d%-13.3f%-10.3f%-7d%-8d%-10.1f%-15.5f%-12.5f"
              % (n, graph.edge_count, dijkstra_ms, bfs_ms, pairs, differ, differ_pct,
                 mean_likely, mean_hops))
        lines.append("%d,%d,%s,%s,%d,%d,%s,%s,%s"
                     % (n, graph.edge_count, dijkstra_ms, bfs_ms, pairs, differ,
                        differ_pct, mean_likely, mean_hops))
    save_csv(folder, "bench_paths.csv", lines)


def bench_allocation(folder):
    instances = 50
    num_wards = 8
    options_per_ward = 4
    budget = 25
    lines = ["instance,dp_value,greedy_value,improvement,improvement_pct"]
    sum_dp = 0.0
    sum_greedy = 0.0
    sum_pct = 0.0
    dp_better = 0
    for i in range(instances):
        # Both methods get the SAME random problem.
        wards = random_allocation_instance(num_wards, options_per_ward, 1000 + i)
        dp_value = dp_allocate(wards, budget).total_value
        greedy_value = greedy_allocate(wards, budget).total_value
        gain = dp_value - greedy_value
        if greedy_value > 0:
            gain_pct = 100.0 * gain / greedy_value
        else:
            gain_pct = 0.0
        lines.append("%d,%s,%s,%s,%s" % (i, dp_value, greedy_value, gain, gain_pct))
        sum_dp += dp_value
        sum_greedy += greedy_value
        sum_pct += gain_pct
        if gain > 1e-9:
            dp_better += 1

    print("\n[3] DP vs greedy allocation: %d random instances, %d wards, %d options, budget %d"
          % (instances, num_wards, options_per_ward, budget))
    print("%-26s%-14s" % ("mean cases averted (DP)", "mean (greedy)"))
    print("%-26.4f%-14.4f" % (sum_dp / instances, sum_greedy / instances))
    print("mean improvement: %.4f cases (%.2f %% per instance on average); "
          "DP strictly better on %d of %d"
          % ((sum_dp - sum_greedy) / instances, sum_pct / instances, dp_better, instances))
    save_csv(folder, "bench_alloc.csv", lines)


if __name__ == "__main__":
    run_full = "--full" in sys.argv
    folder = "results"
    if not os.path.isdir(folder):
        os.makedirs(folder)
    bench_trees(folder, run_full)
    bench_paths(folder)
    bench_allocation(folder)
    print("\nCSV files written to %s/" % folder)
