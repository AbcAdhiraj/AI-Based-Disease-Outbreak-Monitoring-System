# Contact-Network Outbreak Tracing and Resource Allocation System

A Python 3 PBL project (standard library only, no dependencies) that answers three questions about an outbreak:

1. **Store and prioritise** patient records (Unit 1: trees).
2. **Trace exposure** and find the most likely transmission path (Unit 2: graphs).
3. **Allocate scarce supplies** to avert the most infections (Unit 3: dynamic programming).

```
Records -> Unit 1 -> Contact graph -> Unit 2 -> Risk score -> Unit 3 -> Allocation plan
```

The code is written to be easy to read: plain classes and loops, no advanced Python features,
and a comment on each step explaining why it is there.

The AVL tree, the heap, the graph algorithms and the DP are written by hand. `heapq` is used
only inside Dijkstra.

## Unit 1-3 mapping

| Concept | File | Function / class |
|---|---|---|
| AVL tree (insert, delete, search) | `outbreak/avl_tree.py` | `AvlTree.insert`, `remove`, `search` |
| AVL rotations LL, RR, LR, RL | `outbreak/avl_tree.py` | `rotate_ll`, `rotate_rr`, `rotate_lr`, `rotate_rl`, `rebalance` |
| In-order traversal, range query | `outbreak/avl_tree.py` | `AvlTree.inorder`, `range` |
| Balance / BST-order self-check | `outbreak/avl_tree.py` | `AvlTree.validate` |
| Unbalanced BST (benchmark baseline) | `outbreak/bst_baseline.py` | `BstBaseline` |
| Binary max-heap (priority queue) | `outbreak/max_heap.py` | `MaxHeap.push`, `pop`, `peek`, `sift_up`, `sift_down` |
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
- `BstBaseline` insert, search, traversal and height use loops, not recursion, so a 100000-deep chain does
  not hit Python's recursion limit. Its `remove` is recursive and only meant for small trees.
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

### Benchmarks: `python3 benchmarks.py` (mean of 5 runs, about 1 minute total)

```text
[1] AVL vs plain BST, sorted insertions (mean of 5 runs)
n       AVL height  BST height  AVL ms        BST ms        
1000    10          1000        4.202         23.832        
10000   14          10000       53.117        2407.025      
100000  17          skipped     740.784       skipped       

[2] Dijkstra (most likely) vs BFS (fewest hops), average degree 6
nodes   edges    dijkstra ms  bfs ms    pairs  differ  differ %  mean p likely  mean p hops 
1000    3000     1.855        0.396     200    165     82.5      0.06864        0.03024     
10000   30000    66.819       21.178    200    182     91.0      0.02324        0.00843     
100000  300000   918.158      295.715   200    182     91.0      0.01034        0.00326     

[3] DP vs greedy allocation: 50 random instances, 8 wards, 4 options, budget 25
mean cases averted (DP)   mean (greedy) 
46.0924                   40.9954       
mean improvement: 5.0969 cases (12.97 % per instance on average); DP strictly better on 47 of 50
```

What the benchmarks show:

- **AVL vs BST.** On sorted input the plain BST degenerates into a list (height equals n) while the AVL
  height stays logarithmic (10, 14, 17). At n = 10,000 the BST was about 45 times slower.
  The BST at n = 100,000 is `skipped`: it is about 5 x 10^9 steps in pure Python. Run
  `python3 benchmarks.py --full` to measure it.
- **Likely path vs fewest hops.** The two paths differ for 82-91 % of the sampled pairs (200 random
  source/target pairs per size, pairs in different components dropped). The most likely path has roughly
  2-3 times the probability of the fewest-hops path, at about 3-5 times the runtime of a BFS.
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

A patient's id is also the patient's node number in the contact graph,
so the same number links all three units together.
"""


class Patient:
    def __init__(self, id, age, ward, severity):
        self.id = id              # unique key, 0 <= id < number of graph nodes
        self.age = age            # age in years
        self.ward = ward          # ward number, 0 <= ward < number of wards
        self.severity = severity  # 1 (mild) up to 5 (critical)

    def __repr__(self):
        # Only used when printing a Patient while debugging.
        return "Patient(id=%d, age=%d, ward=%d, severity=%d)" % (
            self.id, self.age, self.ward, self.severity)
```

### `outbreak/avl_tree.py`

Unit 1: AVL tree with the four rotations, delete, range query and `validate()`.

```python
"""Unit 1: AVL tree (a self-balancing binary search tree) keyed on patient id.

Idea: a normal BST can become a long chain if keys arrive in sorted order, which
makes search slow (O(n)). An AVL tree fixes this by keeping the heights of the two
subtrees of EVERY node within 1 of each other. It does that with "rotations".
That keeps the tree height about log2(n), so insert/search/delete are O(log n).
"""


class Node:
    def __init__(self, patient):
        self.data = patient   # the Patient record stored here
        self.height = 1       # height of the subtree rooted here (a leaf has height 1)
        self.left = None      # left child (smaller ids)
        self.right = None     # right child (larger ids)


def height_of(node):
    """Height of a subtree; an empty subtree (None) has height 0."""
    if node is None:
        return 0
    return node.height


def update_height(node):
    """Recompute node.height from its two children.  Time: O(1).

    A node is one level taller than its taller child.
    Call this only after the children's heights are already correct.
    """
    left_h = height_of(node.left)
    right_h = height_of(node.right)
    if left_h > right_h:
        node.height = 1 + left_h
    else:
        node.height = 1 + right_h


def balance_factor(node):
    """height(left) - height(right).  An AVL tree keeps this at -1, 0 or +1.

    Positive means the left side is taller, negative means the right is taller.
    """
    if node is None:
        return 0
    return height_of(node.left) - height_of(node.right)


# ---------------------------------------------------------------------------
# The four rotations. Each takes the unbalanced node "z" and returns the node
# that becomes the new root of that part of the tree. All are O(1).
# A rotation only moves a few pointers, and it never changes the left-to-right
# (sorted) order of the keys, so the tree is still a valid BST afterwards.
# ---------------------------------------------------------------------------

def rotate_ll(z):
    """LL case: the left child's LEFT side is too tall -> one right rotation.

              z                 y
             / \\              /   \\
            y   C     ==>     x     z
           / \\                    / \\
          x   B                  B   C

    y moves up and z moves down to be y's right child.
    B holds keys bigger than y but smaller than z, so it fits as z's left child.
    """
    y = z.left          # y will become the new top node
    z.left = y.right    # B moves from y's right to z's left
    y.right = z         # z becomes y's right child
    update_height(z)    # z is now lower than y, so fix z's height first...
    update_height(y)    # ...and then y's height
    return y


def rotate_rr(z):
    """RR case: the right child's RIGHT side is too tall -> one left rotation.

    This is the mirror image of rotate_ll.
    """
    y = z.right         # y will become the new top node
    z.right = y.left    # y's left subtree moves to z's right
    y.left = z          # z becomes y's left child
    update_height(z)
    update_height(y)
    return y


def rotate_lr(z):
    """LR case: the left child's RIGHT side is too tall -> two rotations.

    A single right rotation would not help (the tall part would just move
    over), so first rotate the left child to the left. That turns the zig-zag
    into a straight line (the LL case), then we do the LL rotation.
    """
    z.left = rotate_rr(z.left)   # step 1: rotate the left child left
    return rotate_ll(z)          # step 2: now it is the LL case


def rotate_rl(z):
    """RL case: the right child's LEFT side is too tall -> two rotations.

    Mirror image of rotate_lr.
    """
    z.right = rotate_ll(z.right)  # step 1: rotate the right child right
    return rotate_rr(z)           # step 2: now it is the RR case


def rebalance(node):
    """Fix the node if it became unbalanced; return the (new) top node. O(1).

    One insert or delete changes a subtree height by at most 1, so a node can
    only be out of balance by exactly 2. The sign of the balance factors
    tells us which of the four cases we are in.
    """
    update_height(node)
    bf = balance_factor(node)

    if bf > 1:                              # left side is too tall
        if balance_factor(node.left) >= 0:
            return rotate_ll(node)          # tall part is on the outer (left-left) side
        return rotate_lr(node)              # tall part is on the inner (left-right) side

    if bf < -1:                             # right side is too tall
        if balance_factor(node.right) <= 0:
            return rotate_rr(node)          # outer (right-right) side
        return rotate_rl(node)              # inner (right-left) side

    return node                             # already balanced, nothing to do


class AvlTree:
    def __init__(self):
        self.root = None        # the top node of the tree (None = empty tree)
        self.count = 0          # how many patients are stored
        self.found_flag = False  # helper flag set by insert/remove (see below)

    def __len__(self):
        return self.count

    # ------------------------------------------------------------ insert
    def insert(self, patient):
        """Add a patient. Returns True if the id was new, False if it replaced one.

        Time: O(log n). We walk down like a normal BST insert, then on the way
        back up we call rebalance() on each node we passed. Only nodes on that
        path can have changed height, so those are the only ones to check.
        """
        self.found_flag = False                       # becomes True if the id is new
        self.root = self._insert(self.root, patient)  # the root may change after rotations
        if self.found_flag:
            self.count += 1
        return self.found_flag

    def _insert(self, node, patient):
        if node is None:
            self.found_flag = True        # we reached an empty spot: this id is new
            return Node(patient)

        if patient.id < node.data.id:
            node.left = self._insert(node.left, patient)    # smaller ids go left
        elif patient.id > node.data.id:
            node.right = self._insert(node.right, patient)  # bigger ids go right
        else:
            node.data = patient           # same id already exists: replace the record
            return node

        return rebalance(node)            # fix this node on the way back up

    # ------------------------------------------------------------ remove
    def remove(self, patient_id):
        """Delete the patient with this id. Returns True if it was present.

        Time: O(log n). Same idea as insert: delete like a normal BST, then
        rebalance every node on the path back up.
        """
        self.found_flag = False                          # becomes True if we delete something
        self.root = self._remove(self.root, patient_id)
        if self.found_flag:
            self.count -= 1
        return self.found_flag

    def _remove(self, node, patient_id):
        if node is None:
            return None                   # id not in the tree

        if patient_id < node.data.id:
            node.left = self._remove(node.left, patient_id)
        elif patient_id > node.data.id:
            node.right = self._remove(node.right, patient_id)
        else:
            # We found the node to delete.
            self.found_flag = True
            if node.left is None:
                return node.right         # 0 or 1 child: the child takes its place
            if node.right is None:
                return node.left
            # Two children: copy in the next-larger record (the smallest node
            # of the right subtree), then delete that smaller node instead.
            # This keeps the sorted order correct.
            smallest = node.right
            while smallest.left is not None:
                smallest = smallest.left
            node.data = smallest.data
            saved_flag = self.found_flag
            node.right = self._remove(node.right, smallest.data.id)
            self.found_flag = saved_flag  # the inner call's result must not overwrite ours

        return rebalance(node)

    # ------------------------------------------------------------ search
    def search(self, patient_id):
        """Return the Patient with this id, or None. Time: O(log n).

        At every node we compare and throw away one whole side of the tree,
        and a balanced tree has only about log2(n) levels.
        """
        node = self.root
        while node is not None:
            if patient_id == node.data.id:
                return node.data
            if patient_id < node.data.id:
                node = node.left     # the id can only be in the left part
            else:
                node = node.right    # the id can only be in the right part
        return None

    # --------------------------------------------------------- traversal
    def inorder(self):
        """List of all patients sorted by id. Time: O(n).

        In a BST everything in the left subtree is smaller than the node and
        everything in the right is bigger, so "left, node, right" gives sorted order.
        """
        result = []
        self._inorder(self.root, result)
        return result

    def _inorder(self, node, result):
        if node is None:
            return
        self._inorder(node.left, result)    # 1. everything smaller
        result.append(node.data)            # 2. this node
        self._inorder(node.right, result)   # 3. everything bigger

    def range(self, low, high):
        """All patients with low <= id <= high, sorted. Time: O(log n + k) for k results.

        Same as inorder, but we skip a side when nothing there can be in range.
        """
        result = []
        self._range(self.root, low, high, result)
        return result

    def _range(self, node, low, high, result):
        if node is None:
            return
        if low < node.data.id:                  # the left side may hold ids >= low
            self._range(node.left, low, high, result)
        if low <= node.data.id <= high:         # this node is in range
            result.append(node.data)
        if node.data.id < high:                 # the right side may hold ids <= high
            self._range(node.right, low, high, result)

    # ----------------------------------------------------------- helpers
    def height(self):
        """Height of the whole tree (empty = 0, one node = 1). O(1): it is cached."""
        return height_of(self.root)

    def root_id(self):
        """Id stored at the root, or -1 if empty. Used by tests to see rotations."""
        if self.root is None:
            return -1
        return self.root.data.id

    def validate(self):
        """Check the tree is a correct AVL tree. Returns True/False. Time: O(n).

        For every node we check: (1) its id is between the limits given by its
        ancestors (this proves the order is sorted), (2) its stored height is
        right, (3) the balance factor is -1, 0 or +1.
        """
        result = self._check(self.root, float("-inf"), float("inf"))
        return result != -1

    def _check(self, node, low, high):
        """Returns the true height of the subtree, or -1 if something is wrong."""
        if node is None:
            return 0
        if not (low < node.data.id < high):
            return -1                                   # order violated
        left_h = self._check(node.left, low, node.data.id)    # left ids must be < this id
        right_h = self._check(node.right, node.data.id, high)  # right ids must be > this id
        if left_h == -1 or right_h == -1:
            return -1                                   # a problem deeper down
        if left_h - right_h > 1 or right_h - left_h > 1:
            return -1                                   # not balanced
        real_height = 1 + max(left_h, right_h)
        if node.height != real_height:
            return -1                                   # cached height is wrong
        return real_height
```

### `outbreak/bst_baseline.py`

Unit 1: unbalanced BST, used only as the benchmark baseline.

```python
"""A plain, UNBALANCED binary search tree. Used only as a benchmark baseline.

It has the same functions as AvlTree but never rebalances. If ids arrive in
sorted order every new node goes to the right of the previous one, so the tree
becomes a chain of height n and every insert/search takes O(n).
"""


class BstNode:
    def __init__(self, patient):
        self.data = patient
        self.left = None
        self.right = None


class BstBaseline:
    def __init__(self):
        self.root = None
        self.count = 0
        self.removed = False   # helper flag used by remove()

    def __len__(self):
        return self.count

    def insert(self, patient):
        """Add a patient. True if the id is new, False if it replaced a record.

        Time: O(h) where h is the tree height. h is about log n for random
        input but n for sorted input, so n sorted inserts cost O(n^2) in total.
        We use a loop (not recursion) so a tree 100000 levels deep is no problem.
        """
        if self.root is None:                  # empty tree: the new node is the root
            self.root = BstNode(patient)
            self.count += 1
            return True

        current = self.root
        while True:
            if patient.id == current.data.id:  # id already stored: replace the record
                current.data = patient
                return False
            if patient.id < current.data.id:   # go left
                if current.left is None:       # free spot found: attach the new node
                    current.left = BstNode(patient)
                    self.count += 1
                    return True
                current = current.left
            else:                              # go right
                if current.right is None:
                    current.right = BstNode(patient)
                    self.count += 1
                    return True
                current = current.right

    def remove(self, patient_id):
        """Delete a patient. True if it was present. Time: O(h).

        Recursive, so only use it on small trees (a 100000-deep chain would
        overflow Python's recursion limit). The benchmarks never call it.
        """
        self.removed = False
        self.root = self._remove(self.root, patient_id)
        if self.removed:
            self.count -= 1
        return self.removed

    def _remove(self, node, patient_id):
        if node is None:
            return None
        if patient_id < node.data.id:
            node.left = self._remove(node.left, patient_id)
        elif patient_id > node.data.id:
            node.right = self._remove(node.right, patient_id)
        else:
            self.removed = True
            if node.left is None:      # 0 or 1 child: the child takes its place
                return node.right
            if node.right is None:
                return node.left
            # Two children: copy the next-larger record here, delete that node instead.
            smallest = node.right
            while smallest.left is not None:
                smallest = smallest.left
            node.data = smallest.data
            keep = self.removed
            node.right = self._remove(node.right, smallest.data.id)
            self.removed = keep
        return node

    def search(self, patient_id):
        """Return the Patient with this id or None. Time: O(h)."""
        node = self.root
        while node is not None:
            if patient_id == node.data.id:
                return node.data
            if patient_id < node.data.id:
                node = node.left
            else:
                node = node.right
        return None

    def inorder(self):
        """All patients sorted by id. Time: O(n).

        Uses a stack instead of recursion. We go as far left as possible
        (remembering the nodes on the way), visit a node, then do the same in its
        right subtree. That visits the nodes in sorted order.
        """
        result = []
        stack = []
        node = self.root
        while node is not None or len(stack) > 0:
            while node is not None:        # go left as far as possible
                stack.append(node)
                node = node.left
            node = stack.pop()             # the smallest node not yet visited
            result.append(node.data)
            node = node.right              # then continue with its right subtree
        return result

    def range(self, low, high):
        """Patients with low <= id <= high. Time: O(n) (simply filters the sorted list)."""
        result = []
        for patient in self.inorder():
            if low <= patient.id <= high:
                result.append(patient)
        return result

    def height(self):
        """Height of the tree, counted level by level. Time: O(n)."""
        if self.root is None:
            return 0
        level = [self.root]                # all nodes on the current level
        h = 0
        while len(level) > 0:
            h += 1                         # we are on one more level
            next_level = []
            for node in level:             # collect the children of this level
                if node.left is not None:
                    next_level.append(node.left)
                if node.right is not None:
                    next_level.append(node.right)
            level = next_level
        return h

    def validate(self):
        """True if the ids come out strictly increasing and the count is right."""
        patients = self.inorder()
        for i in range(1, len(patients)):
            if patients[i - 1].id >= patients[i].id:
                return False
        return len(patients) == self.count
```

### `outbreak/max_heap.py`

Unit 1: binary max-heap.

```python
"""Unit 1: binary max-heap of (patient id, risk score).

A max-heap always keeps the item with the BIGGEST score at the top, so we can
get the most at-risk patient instantly. It is stored in a plain list that
represents a "complete" binary tree, level by level:
    parent of position i  -> (i - 1) // 2
    children of position i -> 2*i + 1 and 2*i + 2
Heap rule: every parent has a score >= its children's scores.
"""


class HeapItem:
    def __init__(self, id, score):
        self.id = id          # patient id
        self.score = score    # risk score


class MaxHeap:
    def __init__(self):
        self.items = []       # the heap, stored as a list

    def __len__(self):
        return len(self.items)

    def is_higher(self, a, b):
        """True if item a should be above item b in the heap.

        A bigger score wins. If scores are equal the smaller id wins, which makes
        the order always the same (useful for repeatable results and tests).
        """
        if a.score != b.score:
            return a.score > b.score
        return a.id < b.id

    def sift_up(self, i):
        """Move the item at position i up while it beats its parent. Time: O(log n).

        The heap rule can only be broken between this item and its parent. Each
        swap fixes that pair, and the item goes up one level, at most log2(n) times.
        """
        while i > 0:
            parent = (i - 1) // 2
            if not self.is_higher(self.items[i], self.items[parent]):
                break                                   # parent is already bigger: done
            # swap the item with its parent
            self.items[i], self.items[parent] = self.items[parent], self.items[i]
            i = parent                                  # continue from the new position

    def sift_down(self, i):
        """Move the item at position i down until it beats both children. Time: O(log n)."""
        n = len(self.items)
        while True:
            biggest = i                                 # assume the item is already in place
            left = 2 * i + 1
            right = 2 * i + 2
            if left < n and self.is_higher(self.items[left], self.items[biggest]):
                biggest = left
            if right < n and self.is_higher(self.items[right], self.items[biggest]):
                biggest = right
            if biggest == i:
                break                                   # no child is bigger: done
            # swap with the bigger child (this keeps the rule between the two children)
            self.items[i], self.items[biggest] = self.items[biggest], self.items[i]
            i = biggest

    def push(self, patient_id, score):
        """Add an item. Time: O(log n).

        Put it at the end (this keeps the tree complete) and let it climb up.
        """
        self.items.append(HeapItem(patient_id, score))
        self.sift_up(len(self.items) - 1)

    def pop(self):
        """Remove and return the item with the biggest score. Time: O(log n)."""
        if len(self.items) == 0:
            raise IndexError("pop from empty heap")
        top = self.items[0]                  # the biggest item is always at the root
        last = self.items.pop()              # take the last item off the end...
        if len(self.items) > 0:
            self.items[0] = last             # ...and put it at the root instead
            self.sift_down(0)                # then let it sink to its right place
        return top

    def peek(self):
        """Look at the biggest item without removing it. Time: O(1)."""
        if len(self.items) == 0:
            raise IndexError("peek at empty heap")
        return self.items[0]
```

### `outbreak/graph.py`

Unit 2: contact graph, BFS levels, DFS clusters, Dijkstra with weight `-ln(p)`, hop path.

```python
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
```

### `outbreak/risk.py`

Glue: risk score from Dijkstra output, ward aggregation, heap, supply options.

```python
"""Glue between the units: graph results -> risk scores -> heap and allocation options."""
import math

from .allocation import Option
from .max_heap import MaxHeap

# MODEL ASSUMPTION: each ward can get one of four supply packages.
# More spending averts more cases, but with diminishing returns.
PACKAGE_COSTS = [0, 2, 4, 6]                  # budget units
PACKAGE_EFFECT = [0.0, 0.40, 0.65, 0.80]      # fraction of expected cases averted


def node_risk(graph, infected):
    """Risk of every patient, given the list of infected patients.

    risk(v) = 1 - product over infected sources u of (1 - exp(-dist(u, v)))

    MODEL ASSUMPTION (not validated epidemiology):
      * dist(u, v) from Dijkstra is -ln(probability of the best path u -> v),
        so exp(-dist) is the chance that infection travels from u to v.
      * (1 - that chance) is the chance source u does NOT infect v.
      * Treating sources as independent, the chance that NO source infects v is
        the product of those numbers, and the risk is 1 minus it.
    An infected patient has distance 0 to itself, so its factor is (1 - 1) = 0
    and its risk is exactly 1.
    Time: one Dijkstra per infected source.
    """
    # not_infected[v] = chance that v escapes every source seen so far (starts at 1).
    not_infected = [1.0] * len(graph)
    for source in infected:
        dist = graph.likely_path(source).dist
        for v in range(len(graph)):
            if math.isinf(dist[v]):
                reach = 0.0                   # unreachable: this source cannot infect v
            else:
                reach = math.exp(-dist[v])    # chance that infection reaches v
            not_infected[v] = not_infected[v] * (1.0 - reach)

    risk = []
    for v in range(len(graph)):
        risk.append(1.0 - not_infected[v])
    return risk


def ward_risk(patients, risk, num_wards):
    """Average risk of the patients in each ward (the mean makes wards of
    different sizes comparable)."""
    total = [0.0] * num_wards
    count = [0] * num_wards
    for patient in patients:
        total[patient.ward] += risk[patient.id]
        count[patient.ward] += 1
    result = []
    for w in range(num_wards):
        if count[w] > 0:
            result.append(total[w] / count[w])
        else:
            result.append(0.0)
    return result


def ward_expected_cases(patients, risk, is_infected, num_wards):
    """Expected number of NEW cases in each ward.

    Adding up each patient's risk gives the expected count. Patients who are
    already infected are skipped because their cases cannot be averted.
    """
    expected = [0.0] * num_wards
    for patient in patients:
        if not is_infected[patient.id]:
            expected[patient.ward] += risk[patient.id]
    return expected


def build_risk_heap(risk, is_infected):
    """Put (patient id, risk) into a max-heap, skipping already-infected patients."""
    heap = MaxHeap()
    for v in range(len(risk)):
        if not is_infected[v]:
            heap.push(v, risk[v])
    return heap


def build_ward_options(expected_cases):
    """For each ward, create the four packages. A package averts
    (expected cases of the ward) x (its effect fraction)."""
    wards = []
    for cases in expected_cases:
        options = []
        for k in range(len(PACKAGE_COSTS)):
            options.append(Option(PACKAGE_COSTS[k], cases * PACKAGE_EFFECT[k]))
        wards.append(options)
    return wards
```

### `outbreak/allocation.py`

Unit 3: knapsack DP with backtracking, greedy baseline, brute force, LCS.

```python
"""Unit 3: resource allocation with dynamic programming, plus LCS trend similarity.

Problem: we have several wards and a limited budget. For each ward we may pick
ONE "package" of supplies (each package has a cost and averts some expected
cases). Choose one package per ward so the total cost fits in the budget and
the total number of cases averted is as large as possible.
This is the "multiple-choice knapsack" problem.
"""

NEG = float("-inf")   # marks a table cell that cannot be reached


class Option:
    """One package for a ward: it costs `cost` units and averts `value` cases.

    Every ward should include an Option(0, 0) = "give this ward nothing".
    """

    def __init__(self, cost, value):
        self.cost = cost
        self.value = value


class AllocationPlan:
    """The answer: which option each ward gets, and the totals."""

    def __init__(self, num_wards):
        self.total_value = 0.0
        self.total_cost = 0
        self.choice = [-1] * num_wards   # choice[w] = option index chosen for ward w (-1 = none)
        self.feasible = True             # False if no choice fits within the budget


def make_plan(wards, choice):
    """Build a plan from a list of chosen option indexes and add up the totals."""
    plan = AllocationPlan(len(wards))
    plan.choice = list(choice)
    for w in range(len(wards)):
        if choice[w] >= 0:
            option = wards[w][choice[w]]
            plan.total_cost += option.cost
            plan.total_value += option.value
    return plan


def dp_allocate(wards, budget):
    """Best allocation using dynamic programming.

    Table: dp[i][b] = the most cases we can avert using only the first i wards
    and at most b budget units.
    Recurrence: dp[i][b] = max over the options j of ward i (with cost <= b) of
                           dp[i-1][b - cost_j] + value_j
    In words: try each package for ward i, pay for it, and add the best result
    for the earlier wards with the money that is left.
    Base case: dp[0][b] = 0 (no wards, nothing to gain).
    Time: O(W * B * K) for W wards, budget B and K options per ward.
    Why it is correct: if the whole plan is the best one, then the part of it
    for the first i-1 wards must be the best for the money left; if it were not,
    we could swap in a better part and improve the whole plan. The table stores
    those smaller best answers, so each is calculated only once.
    """
    num_wards = len(wards)

    # dp has num_wards+1 rows and budget+1 columns. NEG = "impossible".
    dp = []
    for i in range(num_wards + 1):
        dp.append([NEG] * (budget + 1))
    # pick[i][b] remembers WHICH option gave dp[i][b], so we can backtrack later.
    pick = []
    for i in range(num_wards + 1):
        pick.append([-1] * (budget + 1))

    # Base case: with zero wards the value is 0 for every budget.
    for b in range(budget + 1):
        dp[0][b] = 0.0

    # Fill the table row by row (ward by ward).
    for i in range(1, num_wards + 1):
        for b in range(budget + 1):
            for j in range(len(wards[i - 1])):
                option = wards[i - 1][j]
                if option.cost > b:
                    continue                          # we cannot afford this option
                before = dp[i - 1][b - option.cost]   # best for earlier wards with what is left
                if before == NEG:
                    continue                          # earlier wards cannot be served
                candidate = before + option.value
                if candidate > dp[i][b]:              # better than anything tried so far
                    dp[i][b] = candidate
                    pick[i][b] = j

    # If even the full budget cannot serve all wards, there is no valid plan.
    if dp[num_wards][budget] == NEG:
        plan = AllocationPlan(num_wards)
        plan.feasible = False
        return plan

    # Backtracking: start at the last ward with the full budget and walk back.
    choice = [-1] * num_wards
    b = budget
    for i in range(num_wards, 0, -1):
        j = pick[i][b]                    # the option chosen for ward i-1 (0-based)
        choice[i - 1] = j
        b = b - wards[i - 1][j].cost      # that option used some budget; the rest is for earlier wards
    return make_plan(wards, choice)


def get_ratio(item):
    """Sorting helper: item is (ratio, ward, option); return its ratio."""
    return item[0]


def greedy_allocate(wards, budget):
    """Baseline: always take the best value-per-cost option that still fits.

    Time: O(N log N) for N options (the sort). It is simple but can be WRONG:
    it never changes its mind, so a cheap option with a great ratio may use up
    money that one big, better option in another ward needed.
    """
    # Step 1: list every option that costs something, with its value/cost ratio.
    items = []
    for w in range(len(wards)):
        for j in range(len(wards[w])):
            option = wards[w][j]
            if option.cost > 0:
                items.append((option.value / option.cost, w, j))

    # Step 2: sort so the best ratio comes first (ties keep their original order).
    items.sort(key=get_ratio, reverse=True)

    # Step 3: walk through the list and take an option if the ward has no
    # package yet and we can still afford it.
    choice = [-1] * len(wards)
    money_left = budget
    for item in items:
        w = item[1]
        j = item[2]
        cost = wards[w][j].cost
        if choice[w] == -1 and cost <= money_left:
            choice[w] = j
            money_left = money_left - cost

    # Step 4: wards still without a package get their best free option, if any.
    for w in range(len(wards)):
        if choice[w] != -1:
            continue
        for j in range(len(wards[w])):
            option = wards[w][j]
            if option.cost == 0:
                if choice[w] == -1 or option.value > wards[w][choice[w]].value:
                    choice[w] = j

    plan = make_plan(wards, choice)
    plan.feasible = (-1 not in choice)
    return plan


def best_from(wards, i, budget_left):
    """Try EVERY combination for wards i, i+1, ... and return (best_value, best_choices).

    Returns (None, None) if no combination fits in budget_left.
    """
    if i == len(wards):
        return 0.0, []                       # no wards left: nothing to choose
    best_value = None
    best_choices = None
    for j in range(len(wards[i])):
        option = wards[i][j]
        if option.cost > budget_left:
            continue                         # too expensive
        sub_value, sub_choices = best_from(wards, i + 1, budget_left - option.cost)
        if sub_value is None:
            continue                         # the later wards cannot be served after this choice
        total = sub_value + option.value
        if best_value is None or total > best_value:
            best_value = total
            best_choices = [j] + sub_choices
    return best_value, best_choices


def brute_force_allocate(wards, budget):
    """Check every possible allocation. Time: O(K^W), so only for tiny test cases.

    We trust it because it tries everything, so there is nothing to get wrong.
    The tests compare the DP result with this one.
    """
    value, choices = best_from(wards, 0, budget)
    if value is None:
        plan = AllocationPlan(len(wards))
        plan.feasible = False
        return plan
    return make_plan(wards, choices)


def lcs_length(a, b):
    """Length of the longest common subsequence of strings a and b.

    A subsequence keeps the letters in order but may skip letters.
    Example: "ABCBDAB" and "BDCABA" share "BCBA" (length 4).
    Table: L[i][j] = LCS length of the first i letters of a and first j of b.
      if a[i-1] == b[j-1]:  L[i][j] = L[i-1][j-1] + 1   (the matching letter extends the answer)
      else:                 L[i][j] = max(L[i-1][j], L[i][j-1])  (skip a letter from a or from b)
    Time: O(len(a) * len(b)).
    """
    # (len(a)+1) x (len(b)+1) table filled with zeros; row 0 and column 0 stay 0
    # because comparing with an empty string gives an LCS of 0.
    table = []
    for i in range(len(a) + 1):
        table.append([0] * (len(b) + 1))

    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            if a[i - 1] == b[j - 1]:
                table[i][j] = table[i - 1][j - 1] + 1
            else:
                table[i][j] = max(table[i - 1][j], table[i][j - 1])
    return table[len(a)][len(b)]


def lcs_similarity(a, b):
    """Similarity between 0 and 1: LCS length divided by the longer string's length.

    1 means identical trends, 0 means nothing in common. Two empty strings count as 1.
    """
    longest = max(len(a), len(b))
    if longest == 0:
        return 1.0
    return lcs_length(a, b) / longest


def discretise_series(series, flat_tolerance=0.05):
    """Turn a list of daily case counts into a string of R, F and D.

    R = rising, F = flat, D = falling; one letter for each day-to-day change.
    We use the RELATIVE change (change divided by yesterday's value) so small and
    large wards can be compared. max(yesterday, 1) avoids dividing by zero.
    A change within +/- flat_tolerance (5% by default) counts as flat.
    """
    letters = ""
    for t in range(1, len(series)):
        yesterday = series[t - 1]
        today = series[t]
        change = (today - yesterday) / max(yesterday, 1.0)
        if change > flat_tolerance:
            letters += "R"
        elif change < -flat_tolerance:
            letters += "D"
        else:
            letters += "F"
    return letters
```

### `outbreak/data_gen.py`

Synthetic graph, patients and case series; optional JHU CSV loader.

```python
"""Synthetic (made-up) data for the project, plus an optional real-data loader.

Every function takes a `seed`. The same seed always gives the same data, so
results can be repeated exactly.
"""
import csv
import os
import random

from .allocation import Option
from .graph import Graph
from .patient import Patient


def generate_contact_graph(n, avg_degree, seed):
    """Random contact graph with n nodes and the given average degree.

    Average degree = 2 * (number of edges) / n, so we need n * avg_degree / 2 edges.
    We repeatedly pick two random different patients and connect them, skipping
    pairs that are already connected.
    Contact duration is random in 0.2..6 hours and proximity in 0.1..1 (assumptions).
    """
    graph = Graph(n)
    if n < 2:
        return graph
    rng = random.Random(seed)
    wanted_edges = int(n * avg_degree / 2)
    most_possible = n * (n - 1) // 2          # a graph cannot have more edges than this
    if wanted_edges > most_possible:
        wanted_edges = most_possible

    used_pairs = set()                        # pairs that already have an edge
    while len(used_pairs) < wanted_edges:
        u = rng.randrange(n)
        v = rng.randrange(n)
        if u == v:
            continue                          # a patient cannot contact themselves
        if u < v:
            pair = (u, v)
        else:
            pair = (v, u)                     # (3, 5) and (5, 3) are the same edge
        if pair in used_pairs:
            continue
        used_pairs.add(pair)
        duration = rng.uniform(0.2, 6.0)
        proximity = rng.uniform(0.1, 1.0)
        graph.add_edge(u, v, duration, proximity)
    return graph


def generate_patients(n, num_wards, seed):
    """n random patients with ids 0..n-1 (the id is also the graph node number)."""
    rng = random.Random(seed)
    patients = []
    for i in range(n):
        age = rng.randint(1, 90)
        ward = rng.randrange(num_wards)
        severity = rng.randint(1, 5)
        patients.append(Patient(i, age, ward, severity))
    return patients


def synthetic_case_series(num_wards, days, seed):
    """Made-up daily case counts, one list per ward.

    Each ward starts at 20..100 cases and changes by its own daily rate
    (between -8% and +12%) plus a little random noise (+/- 5%).
    """
    rng = random.Random(seed)
    all_series = []
    for w in range(num_wards):
        value = rng.uniform(20, 100)
        rate = rng.uniform(-0.08, 0.12)
        series = []
        for d in range(days):
            series.append(value)
            noise = rng.uniform(-0.05, 0.05)
            value = value * (1.0 + rate + noise)
            if value < 0:
                value = 0.0                   # case counts cannot be negative
        all_series.append(series)
    return all_series


def load_jhu_csv(path):
    """Read a Johns Hopkins CSSE file (time_series_covid19_confirmed_global.csv).

    Each row is: Province/State, Country/Region, Lat, Long, then one column per
    date holding the CUMULATIVE confirmed cases. We return one list of numbers per
    row, or [] if the file does not exist or cannot be read.
    (The csv module is used because names like "Korea, South" contain commas.)
    """
    if not os.path.isfile(path):
        return []
    rows = []
    try:
        with open(path, newline="") as f:
            reader = csv.reader(f)
            next(reader, None)                # skip the header line
            for fields in reader:
                if len(fields) <= 4:
                    continue                  # no date columns: skip
                numbers = []
                for text in fields[4:]:       # the first 4 columns are labels
                    if text == "":
                        numbers.append(0.0)
                    else:
                        numbers.append(float(text))
                rows.append(numbers)
    except (OSError, ValueError):
        return []                             # unreadable or malformed file
    return rows


def case_series_for_wards(path, num_wards, days, seed):
    """Daily case series for each ward. Returns (series, used_real_data).

    If the CSV exists and has enough rows and days we use it, converting the
    cumulative totals into daily NEW cases (today minus yesterday, never below 0).
    Otherwise we fall back to synthetic data.
    """
    rows = load_jhu_csv(path)
    enough = len(rows) >= num_wards
    if enough:
        for w in range(num_wards):
            if len(rows[w]) <= days:
                enough = False                # this row has too few days
    if not enough:
        return synthetic_case_series(num_wards, days, seed), False

    series = []
    for w in range(num_wards):
        cumulative = rows[w]
        daily = []
        for t in range(len(cumulative) - days, len(cumulative)):   # the last `days` days
            new_cases = cumulative[t] - cumulative[t - 1]
            if new_cases < 0:
                new_cases = 0.0               # corrections in the data can go negative
            daily.append(new_cases)
        series.append(daily)
    return series, True


def random_allocation_instance(num_wards, options_per_ward, seed):
    """A random knapsack problem for tests and benchmarks.

    Every ward gets Option(0, 0) first, then more options where both cost and
    value increase step by step (so bigger packages avert more cases).
    """
    rng = random.Random(seed)
    wards = []
    for w in range(num_wards):
        options = [Option(0, 0.0)]
        for k in range(1, options_per_ward):
            last = options[-1]
            new_cost = last.cost + rng.randint(1, 4)
            new_value = last.value + rng.uniform(0.5, 6.0)
            options.append(Option(new_cost, new_value))
        wards.append(options)
    return wards
```

### `main.py`

End-to-end pipeline demo.

```python
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

from outbreak.allocation import (Option, brute_force_allocate, discretise_series, dp_allocate,
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
        print("  FAIL", what)


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
            path = g.reconstruct_path(r, src, t)
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
    likely = g.reconstruct_path(g.likely_path(0), 0, 2)
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
    w = [[Option(0, 0), Option(1, 3)],    # ratio 3: greedy grabs it first
         [Option(0, 0), Option(5, 10)]]   # ratio 2: no longer fits afterwards
    dp, gr = dp_allocate(w, 5), greedy_allocate(w, 5)
    check(near(dp.total_value, 10.0) and near(gr.total_value, 3.0))
    check(dp.total_value > gr.total_value and dp.choice == [0, 1])
    for seed in range(100):  # greedy is never better than DP
        r = random_allocation_instance(6, 4, seed)
        check(dp_allocate(r, 15).total_value + 1e-9 >= greedy_allocate(r, 15).total_value)


def test_infeasible():
    w = [[Option(3, 1.0)], [Option(4, 2.0)]]
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
    check(g.edge_count == 3000 and g2.edge_count == 3000 and len(g.adj[10]) == len(g2.adj[10]))
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
```
