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

## Results

All numbers below are copied from real runs in the development container (Python 3.11).
Timings will differ on your machine; the shapes (heights, which method wins) should not.

### Tests: `python3 tests/test_all.py`

```text
[PASS] AVL: sorted 1..1000 stays balanced
[PASS] AVL: four rotations
[PASS] AVL: random insert/delete keep validate()
[PASS] AVL: search and range query
[PASS] Heap: pops in non-increasing order
[PASS] Graph: transmission probability in (0,1]
[PASS] Graph: BFS levels and clusters
[PASS] Graph: Dijkstra == brute force (<= 8 nodes)
[PASS] Graph: likely path differs from fewest-hops path
[PASS] Risk: formula, ward risk, heap
[PASS] Allocation: DP == brute force
[PASS] Allocation: greedy strictly worse than DP
[PASS] Allocation: infeasible budget
[PASS] LCS: known answers and discretiser
[PASS] Data generation and CSV loader

9295 checks, 0 failed
```

### Demo: `python3 main.py`

```text
== Records ==
40 patients stored in AVL tree, height 6, valid=yes

== Contact graph ==
40 nodes, 60 contacts, 3 clusters. Infected sources: 0 and 7
Exposure levels from patient 0 (hops):
  level 1: 5 patients
  level 2: 12 patients
  level 3: 12 patients
  level 4: 8 patients
  unreachable: 2 patients

== Top 5 critical patients (by exposure risk) ==
  id   risk   age   ward  severity
  34   0.923  34    1     2
  29   0.912  30    0     3
  23   0.887  48    2     2
  9    0.792  36    0     2
  13   0.722  49    0     3

== Most likely transmission path to patient 34 ==
Likely path (from source 0): 0 -> 34
  probability 0.8507
Fewest-hops path:            0 -> 34
  probability 0.8507

== Allocation plan (budget 12 units) ==
  ward  ward risk  expected cases  spend  averted
  0     0.390      3.285           4      2.136
  1     0.293      1.756           2      0.702
  2     0.221      1.765           2      0.706
  3     0.260      2.082           4      1.353
  4     0.320      1.237           0      0.000
Total cost 12, total expected cases averted (DP): 4.897
Greedy baseline averts: 4.050

== Trend similarity (synthetic case series) ==
Ward 0 trend: DDDDFDDDDDDDDDDDFDFD
  ward 0: DDDDFDDDDDDDDDDDFDFD  similarity to ward 0 = 1.00
  ward 1: RRRRRRRRRRRRRRRRRRRR  similarity to ward 0 = 0.00
  ward 2: FFFDFFFFDFDFFFFFFFDD  similarity to ward 0 = 0.35
  ward 3: FFDFFFFDDFDFFFDFFDDD  similarity to ward 0 = 0.45
  ward 4: FFRFRFFFFFFFFFFFFFFF  similarity to ward 0 = 0.15
```

### Benchmarks: `python3 benchmarks.py` (mean of 5 runs, about 67 s total)

```text
[1] AVL vs plain BST, sorted insertions (mean of 5 runs)
n       AVL height  BST height  AVL ms        BST ms        
1000    10          1000        6.242         36.265        
10000   14          10000       79.155        3828.646      
100000  17          skipped     1036.156      skipped       

[2] Dijkstra (most likely) vs BFS (fewest hops), average degree 6
nodes   edges    dijkstra ms  bfs ms    pairs  differ  differ %  mean p likely  mean p hops 
1000    3000     2.432        0.401     200    165     82.5      0.06864        0.03024     
10000   30000    57.073       21.069    200    182     91.0      0.02324        0.00843     
100000  300000   863.926      262.875   200    182     91.0      0.01034        0.00326     

[3] DP vs greedy allocation: 50 random instances, 8 wards, 4 options, budget 25
mean cases averted (DP)   mean (greedy) 
46.0924                   40.9954       
mean improvement: 5.0969 cases (12.97 % per instance on average); DP strictly better on 47 of 50
```

What the benchmarks show:

- **AVL vs BST.** On sorted input the plain BST degenerates into a list (height equals n) while the AVL
  height stays logarithmic (10, 14, 17). At n = 10,000 the BST was about 48 times slower.
  The BST at n = 100,000 is `skipped`: it is about 5 x 10^9 steps in pure Python. Run
  `python3 benchmarks.py --full` to measure it.
- **Likely path vs fewest hops.** The two paths differ for 82-91 % of the sampled pairs (200 random
  source/target pairs per size, pairs in different components dropped). The most likely path has roughly
  2-3 times the probability of the fewest-hops path, at about 3-6 times the runtime of a BFS.
  This depends on the synthetic edge probabilities, so it describes this model, not real outbreaks.
- **DP vs greedy.** DP averts a mean of 46.09 cases against 41.00 for greedy (+5.10, about 13 % per
  instance), and is strictly better on 47 of 50 instances. On the other 3 they tie.

CSV versions are written to `results/` when you run the benchmarks (git-ignored).

## Implementation

The full source of every module, in the order data flows through the pipeline.

### `outbreak/patient.py`

Record type shared by all units.

```python
"""The record stored in the AVL tree (Unit 1).

A patient's id is also the patient's node index in the contact graph, so the same
number links all three units together.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Patient:
    id: int        # unique key, 0 <= id < number of graph nodes
    age: int       # years
    ward: int      # ward number, 0 <= ward < number of wards
    severity: int  # 1 (mild) .. 5 (critical)
```

### `outbreak/avl_tree.py`

Unit 1: AVL tree with the four rotations, delete, range query and `validate()`.

```python
"""Unit 1: self-balancing binary search tree keyed on patient id."""
from typing import List, Optional

from .patient import Patient


class _Node:
    __slots__ = ("data", "height", "left", "right")

    def __init__(self, data: Patient):
        self.data = data
        self.height = 1          # cached height: a leaf has height 1
        self.left: Optional["_Node"] = None
        self.right: Optional["_Node"] = None


def _h(n: Optional[_Node]) -> int:
    return n.height if n else 0


def _update_height(n: _Node) -> None:
    """Recompute the cached height from the children. O(1).

    Must be called bottom-up, after the children are already correct.
    """
    n.height = 1 + max(_h(n.left), _h(n.right))


def _balance_factor(n: Optional[_Node]) -> int:
    """height(left) - height(right). AVL invariant: always -1, 0 or +1 (positive = left-heavy)."""
    return _h(n.left) - _h(n.right) if n else 0


def rotate_ll(z: _Node) -> _Node:
    """LL case (left child too tall on its left side): rotate right around z.

            z              y
           / \\           /   \\
          y   C   ==>   x     z
         / \\                 / \\
        x   B               B   C

    Purpose: lift y over z. Complexity O(1).
    Why it works: every key in B lies between y and z, so B can become z's left
    child without breaking BST order, and the tall side (x) rises one level.
    """
    y = z.left
    z.left = y.right
    y.right = z
    _update_height(z)  # z is now lower than y, so fix z first
    _update_height(y)
    return y


def rotate_rr(z: _Node) -> _Node:
    """RR case: mirror image of LL. Rotate left around z. O(1), same order argument."""
    y = z.right
    z.right = y.left
    y.left = z
    _update_height(z)
    _update_height(y)
    return y


def rotate_lr(z: _Node) -> _Node:
    """LR case (left child too tall on its RIGHT side). O(1).

    One right rotation would leave the tall part still too tall, so first turn the
    zig-zag into a straight line (left rotation on the left child), then apply LL.
    """
    z.left = rotate_rr(z.left)
    return rotate_ll(z)


def rotate_rl(z: _Node) -> _Node:
    """RL case: mirror of LR. Right-rotate the right child, then apply RR. O(1)."""
    z.right = rotate_ll(z.right)
    return rotate_rr(z)


def _rebalance(n: _Node) -> _Node:
    """Restore the AVL property at n after one insert/delete below it. O(1).

    Why it works: a single insert/delete changes a subtree height by at most 1,
    so a node can only become off by exactly 2. The signs of the balance factors
    tell us which of the four shapes we are in. ">= 0" / "<= 0" on the child also
    covers the delete-only case where the child is balanced (single rotation).
    """
    _update_height(n)
    bf = _balance_factor(n)
    if bf > 1:
        return rotate_ll(n) if _balance_factor(n.left) >= 0 else rotate_lr(n)
    if bf < -1:
        return rotate_rr(n) if _balance_factor(n.right) <= 0 else rotate_rl(n)
    return n


class AvlTree:
    def __init__(self) -> None:
        self._root: Optional[_Node] = None
        self._count = 0

    def __len__(self) -> int:
        return self._count

    def insert(self, p: Patient) -> bool:
        """Insert a record; True if the id is new, False if it replaced an existing record.

        Complexity O(log n): the tree height is at most ~1.44 log2(n) and each
        rebalance is O(1). Why it works: only nodes on the insertion path change
        height, and _rebalance is applied to each of them bottom-up.
        """
        inserted = [False]

        def go(n: Optional[_Node]) -> _Node:
            if n is None:
                inserted[0] = True
                return _Node(p)
            if p.id < n.data.id:
                n.left = go(n.left)
            elif p.id > n.data.id:
                n.right = go(n.right)
            else:
                n.data = p
                return n
            return _rebalance(n)

        self._root = go(self._root)
        if inserted[0]:
            self._count += 1
        return inserted[0]

    def remove(self, pid: int) -> bool:
        """Delete a key; True if it was present. O(log n).

        A node with two children is replaced by its in-order successor (smallest
        key of the right subtree), which keeps BST order; then the path back up
        is rebalanced.
        """
        removed = [False]

        def go(n: Optional[_Node], key: int) -> Optional[_Node]:
            if n is None:
                return None
            if key < n.data.id:
                n.left = go(n.left, key)
            elif key > n.data.id:
                n.right = go(n.right, key)
            else:
                removed[0] = True
                if n.left is None or n.right is None:
                    return n.left or n.right  # splice out; nothing to rebalance here
                succ = n.right
                while succ.left:
                    succ = succ.left
                n.data = succ.data
                n.right = go(n.right, succ.data.id)
            return _rebalance(n)

        self._root = go(self._root, pid)
        if removed[0]:
            self._count -= 1
        return removed[0]

    def search(self, pid: int) -> Optional[Patient]:
        """Find a record or return None. O(log n): each step discards half the tree."""
        n = self._root
        while n:
            if pid == n.data.id:
                return n.data
            n = n.left if pid < n.data.id else n.right
        return None

    def inorder(self) -> List[Patient]:
        """All records sorted by id. O(n). Left subtree < node < right subtree, so
        left-node-right visits keys in order."""
        out: List[Patient] = []

        def go(n: Optional[_Node]) -> None:
            if n:
                go(n.left)
                out.append(n.data)
                go(n.right)

        go(self._root)
        return out

    def range(self, lo: int, hi: int) -> List[Patient]:
        """Records with lo <= id <= hi, sorted. O(log n + k) for k results.

        We skip the left subtree when node.id <= lo (everything there is smaller)
        and the right subtree when node.id >= hi, so only boundary paths and hits
        are visited.
        """
        out: List[Patient] = []

        def go(n: Optional[_Node]) -> None:
            if n is None:
                return
            if lo < n.data.id:
                go(n.left)
            if lo <= n.data.id <= hi:
                out.append(n.data)
            if n.data.id < hi:
                go(n.right)

        go(self._root)
        return out

    def height(self) -> int:
        """Empty tree = 0, single node = 1. O(1) thanks to the cached height."""
        return _h(self._root)

    def root_id(self) -> int:
        """Id at the root, -1 if empty (used by tests to observe rotations)."""
        return self._root.data.id if self._root else -1

    def validate(self) -> bool:
        """Self-check, O(n): sorted order, correct cached heights, |balance factor| <= 1.

        Each node's key must lie strictly inside the (lo, hi) window inherited from
        its ancestors; that proves the whole tree is sorted.
        """
        def go(n: Optional[_Node], lo: float, hi: float):
            if n is None:
                return 0
            if not (lo < n.data.id < hi):
                return None
            hl = go(n.left, lo, n.data.id)
            hr = go(n.right, n.data.id, hi)
            if hl is None or hr is None:
                return None
            if n.height != 1 + max(hl, hr) or abs(hl - hr) > 1:
                return None
            return n.height

        return go(self._root, float("-inf"), float("inf")) is not None
```

### `outbreak/bst_baseline.py`

Unit 1: unbalanced BST, used only as the benchmark baseline.

```python
"""Plain, UNBALANCED binary search tree: benchmark baseline only.

Same interface as AvlTree but no rebalancing. Sorted input turns it into a linked
list (height n), which is exactly what the benchmark shows. Everything is iterative:
a recursive version would hit Python's recursion limit on a degenerate tree.
"""
from typing import List, Optional

from .patient import Patient


class _Node:
    __slots__ = ("data", "left", "right")

    def __init__(self, data: Patient):
        self.data = data
        self.left: Optional["_Node"] = None
        self.right: Optional["_Node"] = None


class BstBaseline:
    def __init__(self) -> None:
        self._root: Optional[_Node] = None
        self._count = 0

    def __len__(self) -> int:
        return self._count

    def insert(self, p: Patient) -> bool:
        """Standard BST insert. O(h) for tree height h.

        h is ~log n for random input but n for sorted input -> O(n) per insert and
        O(n^2) for n sorted inserts. That is the weakness the AVL tree fixes.
        """
        if self._root is None:
            self._root = _Node(p)
            self._count += 1
            return True
        n = self._root
        while True:
            if p.id == n.data.id:
                n.data = p
                return False
            side = "left" if p.id < n.data.id else "right"
            child = getattr(n, side)
            if child is None:
                setattr(n, side, _Node(p))
                self._count += 1
                return True
            n = child

    def remove(self, pid: int) -> bool:
        """Delete a key. O(h). Same trick as AVL (two children -> in-order successor), no rebalancing."""
        parent, n = None, self._root
        while n and n.data.id != pid:
            parent, n = n, (n.left if pid < n.data.id else n.right)
        if n is None:
            return False
        if n.left and n.right:  # copy successor's record here, then delete the successor node
            sp, s = n, n.right
            while s.left:
                sp, s = s, s.left
            n.data = s.data
            parent, n = sp, s
        child = n.left or n.right  # n now has at most one child
        if parent is None:
            self._root = child
        elif parent.left is n:
            parent.left = child
        else:
            parent.right = child
        self._count -= 1
        return True

    def search(self, pid: int) -> Optional[Patient]:
        """Find a record. O(h)."""
        n = self._root
        while n:
            if pid == n.data.id:
                return n.data
            n = n.left if pid < n.data.id else n.right
        return None

    def inorder(self) -> List[Patient]:
        """Sorted records with an explicit stack. O(n).

        Push the whole left spine; a pop visits the smallest unvisited key, then we
        continue with that node's right subtree.
        """
        out, stack, cur = [], [], self._root
        while cur or stack:
            while cur:
                stack.append(cur)
                cur = cur.left
            cur = stack.pop()
            out.append(cur.data)
            cur = cur.right
        return out

    def range(self, lo: int, hi: int) -> List[Patient]:
        """Ids in [lo, hi]. O(n): a plain filter over the in-order list (AVL prunes and is O(log n + k))."""
        return [p for p in self.inorder() if lo <= p.id <= hi]

    def height(self) -> int:
        """Height, level by level. O(n)."""
        level = [self._root] if self._root else []
        h = 0
        while level:
            h += 1
            level = [c for n in level for c in (n.left, n.right) if c]
        return h

    def validate(self) -> bool:
        """Keys strictly increasing in-order and count consistent."""
        ids = [p.id for p in self.inorder()]
        return all(a < b for a, b in zip(ids, ids[1:])) and len(ids) == self._count
```

### `outbreak/max_heap.py`

Unit 1: binary max-heap.

```python
"""Unit 1: binary max-heap of (patient id, risk score).

Array layout of a complete binary tree: parent(i) = (i-1)//2, children are 2i+1
and 2i+2. No pointers are needed because the tree has no gaps.
"""
from typing import List, NamedTuple


class HeapItem(NamedTuple):
    id: int
    score: float


class MaxHeap:
    def __init__(self) -> None:
        self._items: List[HeapItem] = []

    def __len__(self) -> int:
        return len(self._items)

    @staticmethod
    def _higher(a: HeapItem, b: HeapItem) -> bool:
        """Larger score wins; ties go to the smaller id so pop order is deterministic."""
        if a.score != b.score:
            return a.score > b.score
        return a.id < b.id

    def _sift_up(self, i: int) -> None:
        """Move item i up until its parent is at least as high. O(log n).

        The heap property held everywhere except between i and its parent; each
        swap fixes that pair and only moves the problem one level up.
        """
        a = self._items
        while i > 0:
            parent = (i - 1) // 2
            if not self._higher(a[i], a[parent]):
                break
            a[i], a[parent] = a[parent], a[i]
            i = parent

    def _sift_down(self, i: int) -> None:
        """Move item i down until both children are lower. O(log n).

        Swapping with the HIGHER child keeps the property between that child and
        its sibling, so only one subtree can still be broken.
        """
        a, n = self._items, len(self._items)
        while True:
            best, l, r = i, 2 * i + 1, 2 * i + 2
            if l < n and self._higher(a[l], a[best]):
                best = l
            if r < n and self._higher(a[r], a[best]):
                best = r
            if best == i:
                return
            a[i], a[best] = a[best], a[i]
            i = best

    def push(self, pid: int, score: float) -> None:
        """Insert. O(log n): append at the end (keeps the tree complete), then sift up."""
        self._items.append(HeapItem(pid, score))
        self._sift_up(len(self._items) - 1)

    def pop(self) -> HeapItem:
        """Remove and return the maximum. O(log n).

        Move the last item to the root (keeps the tree complete), shrink, sift down.
        """
        if not self._items:
            raise IndexError("pop from empty heap")
        top = self._items[0]
        last = self._items.pop()
        if self._items:
            self._items[0] = last
            self._sift_down(0)
        return top

    def peek(self) -> HeapItem:
        """Maximum without removing it. O(1): it is always at index 0."""
        if not self._items:
            raise IndexError("peek at empty heap")
        return self._items[0]
```

### `outbreak/graph.py`

Unit 2: contact graph, BFS levels, DFS clusters, Dijkstra with weight `-ln(p)`, hop path.

```python
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
```

### `outbreak/risk.py`

Glue: risk score from Dijkstra output, ward aggregation, heap, supply options.

```python
"""Glue between Unit 2 (graph) and Units 1 and 3."""
import math
from typing import List

from .allocation import Option, WardOptions
from .graph import Graph
from .max_heap import MaxHeap
from .patient import Patient

# MODEL ASSUMPTION: four supply packages per ward with diminishing returns.
PACKAGE_COSTS = (0, 2, 4, 6)
PACKAGE_EFFECT = (0.0, 0.40, 0.65, 0.80)  # fraction of expected cases averted


def node_risk(g: Graph, infected: List[int]) -> List[float]:
    """risk(v) = 1 - prod over infected u of (1 - exp(-dist(u, v))).

    MODEL ASSUMPTION (not validated epidemiology): Dijkstra's dist(u, v) equals
    -ln(probability of the best path u->v), so exp(-dist) is that path's
    probability. "Infection reaches v from u" is that event, and different
    infected sources are treated as independent, giving the usual "at least one
    source succeeds" formula. An infected node has dist 0 to itself, a factor
    (1 - 1) = 0, so its risk is exactly 1.
    Complexity: one Dijkstra per source, O(k (V + E) log V) for k sources.
    """
    survive = [1.0] * len(g)  # probability of escaping every source
    for source in infected:
        dist = g.likely_path(source).dist
        for v, d in enumerate(dist):
            reach = 0.0 if math.isinf(d) else math.exp(-d)
            survive[v] *= 1.0 - reach
    return [1.0 - s for s in survive]


def ward_risk(patients: List[Patient], risk: List[float], num_wards: int) -> List[float]:
    """Mean node risk per ward. O(P). The mean is size-independent, so wards compare fairly."""
    total, count = [0.0] * num_wards, [0] * num_wards
    for p in patients:
        total[p.ward] += risk[p.id]
        count[p.ward] += 1
    return [t / c if c else 0.0 for t, c in zip(total, count)]


def ward_expected_cases(patients: List[Patient], risk: List[float],
                        is_infected: List[bool], num_wards: int) -> List[float]:
    """Expected NEW cases per ward: the sum of risks of not-yet-infected patients
    (linearity of expectation, no independence needed). Infected patients are
    excluded because their cases cannot be "averted"."""
    expected = [0.0] * num_wards
    for p in patients:
        if not is_infected[p.id]:
            expected[p.ward] += risk[p.id]
    return expected


def build_risk_heap(risk: List[float], is_infected: List[bool]) -> MaxHeap:
    """Heap of (patient id, risk) for patients not already infected. O(P log P)."""
    heap = MaxHeap()
    for v, r in enumerate(risk):
        if not is_infected[v]:
            heap.push(v, r)
    return heap


def build_ward_options(expected_cases: List[float]) -> WardOptions:
    """Packages cost 0/2/4/6 units averting 0/40/65/80 % of a ward's expected cases.

    Diminishing returns is what turns the allocation into a real trade-off.
    """
    return [[Option(c, cases * e) for c, e in zip(PACKAGE_COSTS, PACKAGE_EFFECT)]
            for cases in expected_cases]
```

### `outbreak/allocation.py`

Unit 3: knapsack DP with backtracking, greedy baseline, brute force, LCS.

```python
"""Unit 3: resource allocation by dynamic programming, plus LCS trend similarity."""
from dataclasses import dataclass, field
from typing import List, NamedTuple

UNREACHABLE = float("-inf")  # marks dp cells with no valid assignment


class Option(NamedTuple):
    """One way to equip a ward: spend `cost` units, avert `value` expected cases.

    Include a (0, 0) option in every ward so "give this ward nothing" is possible.
    """
    cost: int
    value: float


WardOptions = List[List[Option]]  # [ward][option]


@dataclass
class AllocationPlan:
    total_value: float = 0.0
    total_cost: int = 0
    choice: List[int] = field(default_factory=list)  # option index per ward, -1 = none
    feasible: bool = True                            # False if nothing fits the budget


def _plan_from_choice(wards: WardOptions, choice: List[int]) -> AllocationPlan:
    plan = AllocationPlan(choice=list(choice))
    for ward, j in zip(wards, choice):
        if j >= 0:
            plan.total_cost += ward[j].cost
            plan.total_value += ward[j].value
    return plan


def dp_allocate(wards: WardOptions, budget: int) -> AllocationPlan:
    """Multiple-choice knapsack: exactly one option per ward, total cost <= budget.

    Recurrence:  dp[i][b] = max over options j of ward i with c_ij <= b of
                            dp[i-1][b - c_ij] + v_ij
    where dp[i][b] = best value using the first i wards with at most b budget,
    and dp[0][b] = 0 for every b (no wards, no value).

    Complexity: O(W * B * K) time, O(W * B) memory (W wards, budget B, K options
    per ward); the table is kept so we can backtrack.
    Why it works (optimal substructure): in an optimal plan for the first i
    wards, the choices for the first i-1 wards must themselves be optimal for the
    budget left over, otherwise swapping in a better sub-plan would improve the
    whole plan. The table stores those sub-answers so each is computed once.
    Backtracking: pick[i][b] remembers which option achieved dp[i][b]; walking
    from (W, B) back to 0 and subtracting each chosen cost recovers the plan.
    """
    W = len(wards)
    dp = [[UNREACHABLE] * (budget + 1) for _ in range(W + 1)]
    pick = [[-1] * (budget + 1) for _ in range(W + 1)]
    dp[0] = [0.0] * (budget + 1)
    for i in range(1, W + 1):
        for b in range(budget + 1):
            for j, o in enumerate(wards[i - 1]):
                if o.cost > b or dp[i - 1][b - o.cost] == UNREACHABLE:
                    continue
                candidate = dp[i - 1][b - o.cost] + o.value
                if candidate > dp[i][b]:
                    dp[i][b] = candidate
                    pick[i][b] = j
    if dp[W][budget] == UNREACHABLE:
        return AllocationPlan(choice=[-1] * W, feasible=False)
    choice, b = [-1] * W, budget
    for i in range(W, 0, -1):
        j = pick[i][b]
        choice[i - 1] = j
        b -= wards[i - 1][j].cost
    return _plan_from_choice(wards, choice)


def greedy_allocate(wards: WardOptions, budget: int) -> AllocationPlan:
    """Baseline heuristic. O(N log N) for N = total options.

    Sort every option by value per cost; take an option if its ward has no choice
    yet and it still fits. Why it can be WRONG: it never reconsiders. A cheap
    option with a great ratio can use budget that one bigger, better option
    elsewhere needed, and it cannot upgrade a ward's package. Wards left without
    a choice get their best zero-cost option if one exists.
    """
    items = [(o.value / o.cost, i, j)
             for i, ward in enumerate(wards) for j, o in enumerate(ward) if o.cost > 0]
    items.sort(key=lambda t: -t[0])  # sort is stable, so ties keep input order
    choice, remaining = [-1] * len(wards), budget
    for _, i, j in items:
        if choice[i] == -1 and wards[i][j].cost <= remaining:
            choice[i] = j
            remaining -= wards[i][j].cost
    for i, ward in enumerate(wards):
        if choice[i] != -1:
            continue
        for j, o in enumerate(ward):
            if o.cost == 0 and (choice[i] == -1 or o.value > ward[choice[i]].value):
                choice[i] = j
    plan = _plan_from_choice(wards, choice)
    plan.feasible = -1 not in choice
    return plan


def brute_force_allocate(wards: WardOptions, budget: int) -> AllocationPlan:
    """Ground truth for tests. O(K^W): tiny instances only.

    Trustworthy because it enumerates every assignment, so there is nothing to get wrong.
    """
    best = {"value": float("-inf"), "choice": None}
    current = [-1] * len(wards)

    def search(i: int, left: int, value: float) -> None:
        if i == len(wards):
            if value > best["value"]:
                best["value"], best["choice"] = value, list(current)
            return
        for j, o in enumerate(wards[i]):
            if o.cost <= left:
                current[i] = j
                search(i + 1, left - o.cost, value + o.value)
        current[i] = -1

    search(0, budget, 0.0)
    if best["choice"] is None:
        return AllocationPlan(choice=[-1] * len(wards), feasible=False)
    return _plan_from_choice(wards, best["choice"])


def lcs_length(a: str, b: str) -> int:
    """Length of the longest common subsequence (same order, not nec. adjacent).

    O(n*m) time and memory.
    Recurrence: L[i][j] = L[i-1][j-1] + 1 if a[i-1] == b[j-1],
                else max(L[i-1][j], L[i][j-1]).
    Why it works: if the last letters match, some optimal subsequence can use
    both; if not, at least one of them is unused, so drop it and take the better case.
    """
    L = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            if a[i - 1] == b[j - 1]:
                L[i][j] = L[i - 1][j - 1] + 1
            else:
                L[i][j] = max(L[i - 1][j], L[i][j - 1])
    return L[len(a)][len(b)]


def lcs_similarity(a: str, b: str) -> float:
    """LCS length / length of the longer string, in [0, 1] (two empty strings = 1).

    Dividing by the longer length keeps the score in [0, 1]. O(n*m).
    """
    longest = max(len(a), len(b))
    return 1.0 if longest == 0 else lcs_length(a, b) / longest


def discretise_series(series: List[float], flat_tolerance: float = 0.05) -> str:
    """Turn a case-count series into R (rising) / F (flat) / D (falling), one letter per step.

    O(n). Each step compares day t+1 with day t using the RELATIVE change
    (divided by max(previous, 1), which makes small and large wards comparable
    and avoids dividing by zero). Above +tolerance is R, below -tolerance is D,
    otherwise F.
    """
    out = []
    for prev, cur in zip(series, series[1:]):
        change = (cur - prev) / max(prev, 1.0)
        out.append("R" if change > flat_tolerance else "D" if change < -flat_tolerance else "F")
    return "".join(out)
```

### `outbreak/data_gen.py`

Synthetic graph, patients and case series; optional JHU CSV loader.

```python
"""Synthetic inputs (seeded, reproducible) plus an optional real-data loader."""
import csv
import os
import random
from typing import List, Optional, Tuple

from .allocation import Option, WardOptions
from .graph import Graph
from .patient import Patient


def generate_contact_graph(n: int, avg_degree: float, seed: int) -> Graph:
    """Random graph with about n * avg_degree / 2 distinct undirected edges. O(m).

    Each edge joins two random distinct nodes; a set of used pairs prevents
    duplicates. Average degree = 2m / n, so we draw m = n * avg_degree / 2 edges
    (capped at n(n-1)/2). Duration 0.2..6 h and proximity 0.1..1, uniform: model assumptions.
    """
    g = Graph(n)
    if n < 2:
        return g
    rng = random.Random(seed)
    target = min(n * (n - 1) // 2, int(n * avg_degree / 2))
    used = set()
    while len(used) < target:
        u, v = rng.randrange(n), rng.randrange(n)
        if u == v:
            continue
        key = (u, v) if u < v else (v, u)
        if key in used:
            continue
        used.add(key)
        g.add_edge(u, v, rng.uniform(0.2, 6.0), rng.uniform(0.1, 1.0))
    return g


def generate_patients(n: int, num_wards: int, seed: int) -> List[Patient]:
    """n patients with id = 0..n-1 (id == graph node index)."""
    rng = random.Random(seed)
    return [Patient(i, rng.randint(1, 90), rng.randrange(num_wards), rng.randint(1, 5))
            for i in range(n)]


def synthetic_case_series(num_wards: int, days: int, seed: int) -> List[List[float]]:
    """Fake daily case counts: each ward gets a growth rate in [-8%, +12%] per day,
    +-5% noise, starting from 20..100 cases."""
    rng = random.Random(seed)
    all_series = []
    for _ in range(num_wards):
        value, rate = rng.uniform(20, 100), rng.uniform(-0.08, 0.12)
        series = []
        for _ in range(days):
            series.append(value)
            value = max(0.0, value * (1.0 + rate + rng.uniform(-0.05, 0.05)))
        all_series.append(series)
    return all_series


def load_jhu_csv(path: str) -> List[List[float]]:
    """Read a Johns Hopkins CSSE confirmed-cases CSV (time_series_covid19_confirmed_global.csv).

    Format: Province/State,Country/Region,Lat,Long,<one column per date>...
    The first four columns are labels; the rest are cumulative confirmed counts.
    Returns one cumulative series per row, or [] if the file is missing/unreadable.
    The csv module handles quoted commas such as "Korea, South".
    """
    if not os.path.isfile(path):
        return []
    rows = []
    try:
        with open(path, newline="") as f:
            reader = csv.reader(f)
            next(reader, None)  # header
            for fields in reader:
                if len(fields) > 4:
                    rows.append([float(x) if x else 0.0 for x in fields[4:]])
    except (OSError, ValueError):
        return []
    return rows


def case_series_for_wards(path: str, num_wards: int, days: int,
                          seed: int) -> Tuple[List[List[float]], bool]:
    """Ward trend data: (series, used_real_data).

    Uses the first `num_wards` CSV rows (last `days` days) if the file loads and
    is big enough, converting cumulative totals to daily new cases (negative
    corrections clamp to 0). Otherwise falls back to synthetic series.
    """
    rows = load_jhu_csv(path)
    if len(rows) < num_wards or any(len(r) <= days for r in rows[:num_wards]):
        return synthetic_case_series(num_wards, days, seed), False
    out = []
    for cum in rows[:num_wards]:
        n = len(cum)
        out.append([max(0.0, cum[t] - cum[t - 1]) for t in range(n - days, n)])
    return out, True


def random_allocation_instance(num_wards: int, options_per_ward: int, seed: int) -> WardOptions:
    """Random knapsack instance: every ward has (0,0) plus options with increasing
    cost (+1..4 each step) and value (+0.5..6 each step), so bigger packages avert more."""
    rng = random.Random(seed)
    wards = []
    for _ in range(num_wards):
        options = [Option(0, 0.0)]
        for _ in range(1, options_per_ward):
            last = options[-1]
            options.append(Option(last.cost + rng.randint(1, 4), last.value + rng.uniform(0.5, 6.0)))
        wards.append(options)
    return wards
```

### `main.py`

End-to-end pipeline demo.

```python
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
```

### `tests/test_all.py`

Test suite (no framework).

```python
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
```

### `benchmarks.py`

Benchmarks that write CSVs to `results/`.

```python
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
```
