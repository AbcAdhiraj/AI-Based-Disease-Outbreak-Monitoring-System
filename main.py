"""Run the whole pipeline on a small example and print a report.

    Records -> Unit 1 -> Contact graph -> Unit 2 -> Risk score -> Unit 3 -> Allocation plan

Usage: python3 main.py [path/to/time_series_covid19_confirmed_global.csv]
"""
import sys

from outbreak.allocation import (dp_allocate, greedy_allocate, discretise_series,
                                 lcs_similarity)
from outbreak.avl_tree import AvlTree
from outbreak.data_gen import (case_series_for_wards, generate_contact_graph,
                               generate_patients)
from outbreak.risk import (build_risk_heap, build_ward_options, node_risk,
                           ward_expected_cases, ward_risk)

# Settings for the example.
NUM_PATIENTS = 40
NUM_WARDS = 5
BUDGET = 12            # supply units we can spend in total
DAYS = 21              # length of each ward's case-count series
SEED = 42              # same seed = same result every run
INFECTED = [0, 7]      # patients who are known to be infected


def path_to_text(path):
    """Turn [0, 4, 9] into the text '0 -> 4 -> 9'."""
    if len(path) == 0:
        return "(no path)"
    text = str(path[0])
    for node in path[1:]:
        text += " -> " + str(node)
    return text


def main():
    if len(sys.argv) > 1:
        csv_path = sys.argv[1]
    else:
        csv_path = "time_series_covid19_confirmed_global.csv"

    # ---- UNIT 1: store the patient records in an AVL tree ----
    patients = generate_patients(NUM_PATIENTS, NUM_WARDS, SEED)
    records = AvlTree()
    for i in range(len(patients) - 1, -1, -1):   # insert in DESCENDING id order:
        records.insert(patients[i])              # a plain BST would become a chain here
    print("== Records ==")
    print("%d patients stored in AVL tree, height %d, valid=%s\n"
          % (len(records), records.height(), "yes" if records.validate() else "NO"))

    # ---- UNIT 2: contact graph, exposure levels, clusters ----
    graph = generate_contact_graph(NUM_PATIENTS, 3.0, SEED)
    is_infected = [False] * NUM_PATIENTS
    for p in INFECTED:
        is_infected[p] = True

    clusters = graph.find_clusters()
    print("== Contact graph ==")
    print("%d nodes, %d contacts, %d clusters. Infected sources: %d and %d"
          % (len(graph), graph.edge_count, max(clusters) + 1, INFECTED[0], INFECTED[1]))

    levels = graph.bfs_levels(INFECTED[0])
    print("Exposure levels from patient %d (hops):" % INFECTED[0])
    for level in range(1, max(levels) + 1):
        print("  level %d: %d patients" % (level, levels.count(level)))
    print("  unreachable: %d patients\n" % levels.count(-1))

    # ---- Risk score for every patient, then the heap ----
    risk = node_risk(graph, INFECTED)
    heap = build_risk_heap(risk, is_infected)
    print("== Top 5 critical patients (by exposure risk) ==")
    print("  %-4s %-6s %-5s %-5s %s" % ("id", "risk", "age", "ward", "severity"))
    target = None
    shown = 0
    while shown < 5 and len(heap) > 0:
        top = heap.pop()                  # always the highest remaining risk
        if shown == 0:
            target = top.id               # remember the most at-risk patient
        patient = records.search(top.id)  # look the full record up in the AVL tree
        print("  %-4d %-6.3f %-5d %-5d %d"
              % (top.id, top.score, patient.age, patient.ward, patient.severity))
        shown += 1

    # ---- Most likely transmission path to that patient ----
    print("\n== Most likely transmission path to patient %d ==" % target)
    # Run Dijkstra from each infected patient and use the source closest to the target.
    best_source = INFECTED[0]
    best_result = graph.likely_path(best_source)
    for source in INFECTED[1:]:
        result = graph.likely_path(source)
        if result.dist[target] < best_result.dist[target]:
            best_source = source
            best_result = result
    likely = graph.reconstruct_path(best_result, best_source, target)
    hops = graph.hop_path(best_source, target)
    print("Likely path (from source %d): %s" % (best_source, path_to_text(likely)))
    print("  probability %.4f" % graph.path_probability(likely))
    print("Fewest-hops path:            %s" % path_to_text(hops))
    print("  probability %.4f\n" % graph.path_probability(hops))

    # ---- UNIT 3: allocate the supplies ----
    ward_scores = ward_risk(patients, risk, NUM_WARDS)
    expected = ward_expected_cases(patients, risk, is_infected, NUM_WARDS)
    options = build_ward_options(expected)
    dp_plan = dp_allocate(options, BUDGET)
    greedy_plan = greedy_allocate(options, BUDGET)
    print("== Allocation plan (budget %d units) ==" % BUDGET)
    print("  %-5s %-10s %-15s %-6s %s" % ("ward", "ward risk", "expected cases", "spend", "averted"))
    for w in range(NUM_WARDS):
        chosen = options[w][dp_plan.choice[w]]
        print("  %-5d %-10.3f %-15.3f %-6d %.3f"
              % (w, ward_scores[w], expected[w], chosen.cost, chosen.value))
    print("Total cost %d, total expected cases averted (DP): %.3f"
          % (dp_plan.total_cost, dp_plan.total_value))
    print("Greedy baseline averts: %.3f\n" % greedy_plan.total_value)

    # ---- LCS: which ward's case trend looks like the riskiest ward's trend? ----
    series, used_real = case_series_for_wards(csv_path, NUM_WARDS, DAYS, SEED)
    riskiest = 0
    for w in range(1, NUM_WARDS):
        if ward_scores[w] > ward_scores[riskiest]:
            riskiest = w
    reference = discretise_series(series[riskiest])
    if used_real:
        source_name = "real CSV"
    else:
        source_name = "synthetic"
    print("== Trend similarity (%s case series) ==" % source_name)
    print("Ward %d trend: %s" % (riskiest, reference))
    for w in range(NUM_WARDS):
        trend = discretise_series(series[w])
        print("  ward %d: %s  similarity to ward %d = %.2f"
              % (w, trend, riskiest, lcs_similarity(reference, trend)))


if __name__ == "__main__":
    main()
