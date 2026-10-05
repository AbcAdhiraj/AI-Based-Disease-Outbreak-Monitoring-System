"""Run Records -> Unit 1 -> Contact graph -> Unit 2 -> Risk -> Unit 3 -> Plan on a small example.

Usage: python3 main.py [path/to/time_series_covid19_confirmed_global.csv]
"""
import sys

from outbreak.allocation import dp_allocate, discretise_series, greedy_allocate, lcs_similarity
from outbreak.avl_tree import AvlTree
from outbreak.data_gen import case_series_for_wards, generate_contact_graph, generate_patients
from outbreak.graph import Graph
from outbreak.risk import (build_risk_heap, build_ward_options, node_risk,
                           ward_expected_cases, ward_risk)

PATIENTS, WARDS, BUDGET, DAYS, SEED = 40, 5, 12, 21, 42
INFECTED = [0, 7]


def path_text(path):
    return " -> ".join(map(str, path)) if path else "(no path)"


def main() -> None:
    csv_path = sys.argv[1] if len(sys.argv) > 1 else "time_series_covid19_confirmed_global.csv"

    # ---- Unit 1: records in an AVL tree ----
    patients = generate_patients(PATIENTS, WARDS, SEED)
    records = AvlTree()
    for p in reversed(patients):  # descending ids: worst case for a plain BST
        records.insert(p)
    print("== Records ==")
    print(f"{len(records)} patients stored in AVL tree, height {records.height()}, "
          f"valid={'yes' if records.validate() else 'NO'}\n")

    # ---- Unit 2: contact graph, exposure levels, clusters ----
    g = generate_contact_graph(PATIENTS, 3.0, SEED)
    is_infected = [v in INFECTED for v in range(PATIENTS)]
    clusters = g.find_clusters()
    print("== Contact graph ==")
    print(f"{len(g)} nodes, {g.edge_count} contacts, {max(clusters) + 1} clusters. "
          f"Infected sources: {INFECTED[0]} and {INFECTED[1]}")
    level = g.bfs_levels(INFECTED[0])
    print(f"Exposure levels from patient {INFECTED[0]} (hops):")
    for l in range(1, max(level) + 1):
        print(f"  level {l}: {level.count(l)} patients")
    print(f"  unreachable: {level.count(-1)} patients\n")

    # ---- Risk glue + heap ----
    risk = node_risk(g, INFECTED)
    heap = build_risk_heap(risk, is_infected)
    print("== Top 5 critical patients (by exposure risk) ==")
    print(f"  {'id':<4} {'risk':<6} {'age':<5} {'ward':<5} severity")
    target = None
    for k in range(min(5, len(heap))):
        top = heap.pop()
        target = top.id if k == 0 else target
        p = records.search(top.id)
        print(f"  {top.id:<4} {top.score:<6.3f} {p.age:<5} {p.ward:<5} {p.severity}")

    # ---- Most likely path to the top patient ----
    print(f"\n== Most likely transmission path to patient {target} ==")
    results = {s: g.likely_path(s) for s in INFECTED}
    best_source = min(INFECTED, key=lambda s: results[s].dist[target])
    likely = Graph.reconstruct_path(results[best_source], best_source, target)
    hops = g.hop_path(best_source, target)
    print(f"Likely path (from source {best_source}): {path_text(likely)}")
    print(f"  probability {g.path_probability(likely):.4f}")
    print(f"Fewest-hops path:            {path_text(hops)}")
    print(f"  probability {g.path_probability(hops):.4f}\n")

    # ---- Unit 3: allocation ----
    wr = ward_risk(patients, risk, WARDS)
    expected = ward_expected_cases(patients, risk, is_infected, WARDS)
    options = build_ward_options(expected)
    dp, greedy = dp_allocate(options, BUDGET), greedy_allocate(options, BUDGET)
    print(f"== Allocation plan (budget {BUDGET} units) ==")
    print(f"  {'ward':<5} {'ward risk':<10} {'expected cases':<15} {'spend':<6} averted")
    for w in range(WARDS):
        o = options[w][dp.choice[w]]
        print(f"  {w:<5} {wr[w]:<10.3f} {expected[w]:<15.3f} {o.cost:<6} {o.value:.3f}")
    print(f"Total cost {dp.total_cost}, total expected cases averted (DP): {dp.total_value:.3f}")
    print(f"Greedy baseline averts: {greedy.total_value:.3f}\n")

    # ---- LCS: which ward's trend looks like the riskiest ward's trend? ----
    series, real = case_series_for_wards(csv_path, WARDS, DAYS, SEED)
    riskiest = max(range(WARDS), key=lambda w: wr[w])
    ref = discretise_series(series[riskiest])
    print(f"== Trend similarity ({'real CSV' if real else 'synthetic'} case series) ==")
    print(f"Ward {riskiest} trend: {ref}")
    for w in range(WARDS):
        t = discretise_series(series[w])
        print(f"  ward {w}: {t}  similarity to ward {riskiest} = {lcs_similarity(ref, t):.2f}")


if __name__ == "__main__":
    main()
