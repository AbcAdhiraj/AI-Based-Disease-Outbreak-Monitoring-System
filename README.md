# Contact-Network Outbreak Tracing and Resource Allocation System

A Python 3 PBL project (standard library only, no dependencies) that answers three questions about an outbreak:

1. **Store and prioritise** patient records (Unit 1: trees).
2. **Trace exposure** and find the most likely transmission path (Unit 2: graphs).
3. **Allocate scarce supplies** to avert the most infections (Unit 3: dynamic programming).

```
Records -> Unit 1 -> Contact graph -> Unit 2 -> Risk score -> Unit 3 -> Allocation plan
```

The AVL tree, the heap, the graph algorithms and the DP are written by hand. `heapq` is used
only inside Dijkstra.

## Unit 1-3 mapping

| Concept | File | Function / class |
|---|---|---|
| AVL tree (insert, delete, search) | `outbreak/avl_tree.py` | `AvlTree.insert`, `remove`, `search` |
| AVL rotations LL, RR, LR, RL | `outbreak/avl_tree.py` | `rotate_ll`, `rotate_rr`, `rotate_lr`, `rotate_rl`, `_rebalance` |
| In-order traversal, range query | `outbreak/avl_tree.py` | `AvlTree.inorder`, `range` |
| Balance / BST-order self-check | `outbreak/avl_tree.py` | `AvlTree.validate` |
| Unbalanced BST (benchmark baseline) | `outbreak/bst_baseline.py` | `BstBaseline` |
| Binary max-heap (priority queue) | `outbreak/max_heap.py` | `MaxHeap.push`, `pop`, `peek`, `_sift_up`, `_sift_down` |
| Adjacency-list graph, edge weights | `outbreak/graph.py` | `Graph.add_edge`, `transmission_probability` |
| BFS exposure levels | `outbreak/graph.py` | `Graph.bfs_levels` |
| DFS clusters (connected components) | `outbreak/graph.py` | `Graph.find_clusters` |
| Dijkstra, weight `-ln(p)` | `outbreak/graph.py` | `Graph.likely_path`, `reconstruct_path` |
| Fewest-hops baseline | `outbreak/graph.py` | `Graph.hop_path` |
| Risk from Dijkstra output, heap of risks | `outbreak/risk.py` | `node_risk`, `ward_risk`, `build_risk_heap` |
| Multiple-choice knapsack DP + backtracking | `outbreak/allocation.py` | `dp_allocate` |
| Greedy baseline, brute-force checker | `outbreak/allocation.py` | `greedy_allocate`, `brute_force_allocate` |
| LCS, trend discretisation (R/F/D) | `outbreak/allocation.py` | `lcs_length`, `lcs_similarity`, `discretise_series` |
| Synthetic data, JHU CSV loader | `outbreak/data_gen.py` | `generate_contact_graph`, `generate_patients`, `load_jhu_csv` |
| End-to-end pipeline report | `main.py` | `main` |

## Run

Requires Python 3.8+ (developed on 3.11). No install step.

```bash
python3 main.py                      # pipeline demo
python3 main.py path/to/time_series_covid19_confirmed_global.csv   # optional real case series
```

`main.py` looks for `time_series_covid19_confirmed_global.csv` (Johns Hopkins CSSE format) in the
current directory if no path is given, and falls back to synthetic series if it is missing.

## Tests

```bash
python3 tests/test_all.py            # prints PASS/FAIL per group, exit code 1 on any failure
```

No test framework is used; `check(...)` is a small assert-style helper.

## Benchmarks

```bash
python3 benchmarks.py                # writes results/bench_*.csv and prints three tables
python3 benchmarks.py --full         # also times the plain BST at n = 100000 (very slow)
```

Each timing is the mean of 5 repeats on identical inputs. Nothing is hard-coded.
Plain-BST insertion of 100000 sorted keys is O(n^2), about 5 x 10^9 steps. That takes many minutes
per repeat in pure Python, so that one cell is **skipped by default** and shown as `skipped`.
Use `--full` to measure it.

## Design decisions and limitations

- **All data is synthetic** (seeded random graph, patients, case series) unless you supply the JHU CSV.
  Results describe the algorithms, not a real outbreak.
- **The formulas are model assumptions, not validated epidemiology.**
  - Edge probability: `p = 1 - exp(-0.35 * duration * proximity)`, clamped to `[1e-6, 1]` (`transmission_probability`).
  - Node risk: `risk(v) = 1 - prod_u (1 - exp(-dist(u, v)))`, assuming independent infected sources and independent hops.
  - Ward options: costs 0/2/4/6 avert 0/40/65/80 % of expected cases (`build_ward_options`).
- `patient id == graph node index`, which links the three units without a lookup table.
- The DP needs a `(0, 0)` option in each ward to allow "no supplies"; costs are integers.
- The greedy baseline never upgrades a ward's package. That is the weakness the DP fixes.
- `BstBaseline` is fully iterative so a degenerate tree does not hit Python's recursion limit.
  The AVL tree uses recursion, which is safe because its depth is O(log n).
- The random graph connects uniformly random pairs, so it has no community structure.
- Python is much slower than compiled code. Compare the methods with each other, not with
  C++ numbers from other sources.

## Measured results (fill in from your own run)

| Experiment | Your measured result |
|---|---|
| AVL vs BST height, n = 1e3 / 1e4 / 1e5 | _paste from `results/bench_tree.csv`_ |
| AVL vs BST insert time | _paste_ |
| Dijkstra vs BFS runtime by graph size | _paste from `results/bench_paths.csv`_ |
| % of pairs where likely path differs from fewest-hops path | _paste_ |
| DP vs greedy: mean cases averted, mean improvement | _paste from `results/bench_alloc.csv`_ |

Record your machine (CPU, Python version) next to these numbers.
