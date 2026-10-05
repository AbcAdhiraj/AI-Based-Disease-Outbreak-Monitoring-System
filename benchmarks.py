"""Benchmarks. Every number printed or written to CSV comes from a real run here.

Usage: python3 benchmarks.py [--full] [--out results]
Each timing is repeated REPS times on identical inputs and the mean is reported.

Plain-BST insertion of 100000 SORTED keys is ~5 * 10^9 loop steps (O(n^2)), which in
pure Python takes many minutes per repeat, so that single cell is skipped unless you
pass --full. Skipped cells are shown as "skipped" and never filled with invented numbers.
"""
import argparse
import os
import random
import time

from outbreak.allocation import dp_allocate, greedy_allocate
from outbreak.avl_tree import AvlTree
from outbreak.bst_baseline import BstBaseline
from outbreak.data_gen import generate_contact_graph, random_allocation_instance
from outbreak.graph import Graph
from outbreak.patient import Patient

REPS = 5


def mean_ms(fn) -> float:
    """Run fn() REPS times; return the mean wall-clock time in milliseconds."""
    total = 0.0
    for _ in range(REPS):
        t0 = time.perf_counter()
        fn()
        total += time.perf_counter() - t0
    return total / REPS * 1000.0


def bench_trees(out_dir: str, full: bool) -> None:
    print(f"\n[1] AVL vs plain BST, sorted insertions (mean of {REPS} runs)")
    print(f"{'n':<8}{'AVL height':<12}{'BST height':<12}{'AVL ms':<14}{'BST ms':<14}")
    rows = ["n,avl_height,bst_height,avl_ms,bst_ms"]
    for n in (1000, 10000, 100000):
        data = [Patient(i, 40, i % 5, 1 + i % 5) for i in range(n)]  # identical input for both
        h = {}

        def build_avl():
            t = AvlTree()
            for p in data:
                t.insert(p)
            h["avl"] = t.height()

        def build_bst():
            t = BstBaseline()
            for p in data:
                t.insert(p)
            h["bst"] = t.height()

        avl_ms = mean_ms(build_avl)
        if n == 100000 and not full:
            bst_h, bst_ms = "skipped", "skipped"
        else:
            bst_ms = mean_ms(build_bst)
            bst_h = h["bst"]
        bst_ms_txt = bst_ms if isinstance(bst_ms, str) else f"{bst_ms:.3f}"
        print(f"{n:<8}{h['avl']:<12}{bst_h:<12}{avl_ms:<14.3f}{bst_ms_txt:<14}")
        rows.append(f"{n},{h['avl']},{bst_h},{avl_ms},{bst_ms}")
    write_csv(out_dir, "bench_tree.csv", rows)


def bench_paths(out_dir: str) -> None:
    sources, targets_per_source = 20, 10  # up to 200 (source, target) pairs per size
    print("\n[2] Dijkstra (most likely) vs BFS (fewest hops), average degree 6")
    print(f"{'nodes':<8}{'edges':<9}{'dijkstra ms':<13}{'bfs ms':<10}{'pairs':<7}"
          f"{'differ':<8}{'differ %':<10}{'mean p likely':<15}{'mean p hops':<12}")
    rows = ["nodes,edges,dijkstra_ms,bfs_ms,pairs,paths_differ,differ_pct,mean_p_likely,mean_p_hops"]
    for n in (1000, 10000, 100000):
        g = generate_contact_graph(n, 6.0, 99)
        dijkstra_ms = mean_ms(lambda: g.likely_path(0))
        bfs_ms = mean_ms(lambda: g.bfs_levels(0))  # single-source, like Dijkstra
        rng = random.Random(123)
        pairs = differ = 0
        sum_likely = sum_hops = 0.0
        for _ in range(sources):
            s = rng.randrange(n)
            result = g.likely_path(s)
            for _ in range(targets_per_source):
                t = rng.randrange(n)
                if t == s:
                    continue
                likely = Graph.reconstruct_path(result, s, t)
                if not likely:
                    continue  # other component: nothing to compare
                hops = g.hop_path(s, t)
                pairs += 1
                differ += likely != hops
                sum_likely += g.path_probability(likely)
                sum_hops += g.path_probability(hops)
        pct = 100.0 * differ / pairs if pairs else 0.0
        mp_l, mp_h = (sum_likely / pairs, sum_hops / pairs) if pairs else (0.0, 0.0)
        print(f"{n:<8}{g.edge_count:<9}{dijkstra_ms:<13.3f}{bfs_ms:<10.3f}{pairs:<7}"
              f"{differ:<8}{pct:<10.1f}{mp_l:<15.5f}{mp_h:<12.5f}")
        rows.append(f"{n},{g.edge_count},{dijkstra_ms},{bfs_ms},{pairs},{differ},{pct},{mp_l},{mp_h}")
    write_csv(out_dir, "bench_paths.csv", rows)


def bench_allocation(out_dir: str) -> None:
    instances, wards, options, budget = 50, 8, 4, 25
    rows = ["instance,dp_value,greedy_value,improvement,improvement_pct"]
    sum_dp = sum_greedy = sum_pct = 0.0
    dp_better = 0
    for i in range(instances):
        w = random_allocation_instance(wards, options, 1000 + i)  # same instance for both methods
        dp = dp_allocate(w, budget).total_value
        greedy = greedy_allocate(w, budget).total_value
        gain = dp - greedy
        pct = 100.0 * gain / greedy if greedy > 0 else 0.0
        rows.append(f"{i},{dp},{greedy},{gain},{pct}")
        sum_dp, sum_greedy, sum_pct = sum_dp + dp, sum_greedy + greedy, sum_pct + pct
        dp_better += gain > 1e-9
    print(f"\n[3] DP vs greedy allocation: {instances} random instances, {wards} wards, "
          f"{options} options, budget {budget}")
    print(f"{'mean cases averted (DP)':<26}{'mean (greedy)':<14}")
    print(f"{sum_dp / instances:<26.4f}{sum_greedy / instances:<14.4f}")
    print(f"mean improvement: {(sum_dp - sum_greedy) / instances:.4f} cases "
          f"({sum_pct / instances:.2f} % per instance on average); "
          f"DP strictly better on {dp_better} of {instances}")
    write_csv(out_dir, "bench_alloc.csv", rows)


def write_csv(out_dir: str, name: str, rows) -> None:
    with open(os.path.join(out_dir, name), "w") as f:
        f.write("\n".join(rows) + "\n")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--full", action="store_true", help="also time plain BST at n=100000 (very slow)")
    ap.add_argument("--out", default="results", help="output directory for CSV files")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    bench_trees(args.out, args.full)
    bench_paths(args.out)
    bench_allocation(args.out)
    print(f"\nCSV files written to {args.out}/")
