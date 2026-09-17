# AI-Based Disease Outbreak Monitoring System

## Extreme-Detail Study and Explanation Guide

### Based on the DSA Progress Report -- I

> **Course:** Data Structures and Algorithms -- II\
> **Course Code:** CCSE0301\
> **Program:** BTech CSE\
> **Student:** Adhiraj Tiwari\
> **Roll No.:** 2501330100029\
> **Faculty:** Dr. Shamshad Ali\
> **Project:** AI-Based Disease Outbreak Monitoring System\
> **Reporting Month:** Month 1\
> **Report Date:** 12 September 2026

------------------------------------------------------------------------

# 1. What This Project Is Actually About

The project is an **AI-Based Disease Outbreak Monitoring System** whose
central technical idea is to treat outbreak monitoring as a
**data-structures and algorithms problem**.

The system is designed around three major questions:

1.  **Who is linked to whom?**
2.  **How can infection move through those links?**
3.  **How should limited medical resources be allocated?**

The report proposes solving these questions using different data
structures and algorithms:

  Problem                         Main DSA idea
  ------------------------------- ------------------------------------
  Patient-record lookup           AVL trees and B+ trees
  Critical-case prioritisation    Heaps
  Contact tracing                 Graphs
  Exposure levels                 BFS
  Cluster detection               DFS
  Transmission-path estimation    Dijkstra
  Resource allocation             Dynamic Programming / 0/1 Knapsack
  District zoning                 Graph Colouring
  Collection-route optimisation   Branch-and-Bound / TSP
  Large disk-backed indexes       B-trees / B+ trees
  Advanced priority structures    Binomial and Fibonacci heaps
  Timeline comparison             Longest Common Subsequence
  Multi-stage optimisation        Matrix Chain Multiplication
  Network-wide reachability       Transitive Closure
  Minimum-cost connectivity       Prim's / Kruskal's

The important point is that the project is **not claiming that every
algorithm is simultaneously necessary for a production epidemiological
system**. It is structured as a DSA-II academic project in which
concepts from Units 1--5 are mapped onto realistic computational
problems.

------------------------------------------------------------------------

# 2. The Core Architecture

At a conceptual level, the system can be understood as four connected
modules:

``` text
                    AI-Based Disease Outbreak
                         Monitoring System
                                  |
             +--------------------+--------------------+
             |                    |                    |
         Indexing            Contact Graph         Allocation
             |                    |                    |
       AVL / B+ Trees       BFS / DFS / Dijkstra   Dynamic Programming
       Heaps                MST / Closure          0/1 Knapsack
             |                    |                    |
             +--------------------+--------------------+
                                  |
                             Scheduling
                                  |
                   Graph Colouring / TSP /
                   Backtracking / B&B
```

The four modules are:

1.  **Indexing**
2.  **Contact graph**
3.  **Resource allocation**
4.  **Scheduling**

Each module exists because it solves a different computational problem.

------------------------------------------------------------------------

# 3. Why Data Structures Matter in an Outbreak System

Suppose a surveillance system contains millions of patient records.

A naive implementation could store records in a normal list:

``` text
[Patient 1, Patient 2, Patient 3, ..., Patient n]
```

If a new query asks:

> Find patient 4,120,391.

A linear search could require checking a large fraction of the records.

Its worst-case complexity is:

\[ O(n) \]

For very large `n`, this becomes expensive.

A balanced search tree can instead keep the height approximately
logarithmic.

For an AVL tree:

\[ O(`\log `{=tex}n) \]

search, insertion and deletion are the intended complexity.

That difference becomes increasingly important as the dataset grows.

For example, conceptually:

``` text
Linear structure:
1 -> 2 -> 3 -> 4 -> ... -> n

Balanced tree:
                 50
              /      \
            25        75
           /  \      /  \
         12   37   62   87
```

The tree does not need to inspect every record.

This is the project's fundamental DSA argument:

> The outbreak problem produces large, dynamic, interconnected datasets,
> so choosing appropriate data structures can make important operations
> substantially more efficient.

------------------------------------------------------------------------

# 4. Module 1 --- Patient Record Indexing

## 4.1 What Is an Index?

An index is a structure that makes finding information faster.

Consider patient records:

``` text
Patient ID
Name
Age
Location
Diagnosis
Date
Status
```

If the system stores records according to a key such as:

``` text
Patient ID
```

the data structure can organise records so that queries do not require a
full scan.

The report proposes:

-   AVL trees
-   B+ trees
-   Heaps

------------------------------------------------------------------------

# 5. Binary Trees

A **tree** is a hierarchical data structure made of nodes connected by
edges.

Unlike a general graph, a tree has a specific structure:

-   There is a root.
-   Every node except the root has a parent.
-   Nodes can have children.
-   A tree contains no cycles.

Example:

``` text
             A
           /   \
          B     C
        /  \     \
       D    E     F
```

Here:

-   `A` is the root.
-   `B` and `C` are children of `A`.
-   `D` and `E` are children of `B`.
-   `F` is a child of `C`.
-   `D`, `E`, and `F` are leaves.

------------------------------------------------------------------------

# 6. Important Tree Terminology

## Root

The topmost node.

In the example:

``` text
A
```

is the root.

## Parent

A node directly above another node.

`A` is the parent of `B`.

## Child

A node directly below another node.

`B` is a child of `A`.

## Leaf

A node with no children.

`D`, `E`, and `F` are leaves.

## Internal Node

A node with at least one child.

`A`, `B`, and `C` are internal nodes.

## Edge

The connection between two nodes.

## Degree of a Node

The number of children of that node.

## Depth

The number of edges from the root to a node.

If:

``` text
A
|
B
|
D
```

then:

-   depth(A) = 0
-   depth(B) = 1
-   depth(D) = 2

## Height

The longest path from a node to a leaf.

The height of a tree is the height of its root.

------------------------------------------------------------------------

# 7. Binary Tree

A binary tree is a tree in which each node can have at most two
children.

Those children are normally called:

-   left child
-   right child

Example:

``` text
        10
       /  \
      5    15
     / \     \
    2   7     20
```

A binary tree is not necessarily sorted.

That distinction is important.

------------------------------------------------------------------------

# 8. Binary Search Tree

A **Binary Search Tree (BST)** imposes an ordering rule.

For every node:

``` text
values in left subtree < node < values in right subtree
```

Example:

``` text
          50
        /    \
      30      70
     /  \    /  \
   20   40  60   80
```

Everything to the left of `50` is smaller.

Everything to the right is larger.

This property enables searching.

------------------------------------------------------------------------

# 9. Searching in a BST

Suppose we want to find `60`.

Start at:

``` text
50
```

Since:

``` text
60 > 50
```

go right.

Now:

``` text
70
```

Since:

``` text
60 < 70
```

go left.

Now:

``` text
60
```

Found.

Instead of examining every node, the algorithm eliminates an entire
subtree at every decision.

If the tree is balanced, the height is approximately:

\[ O(`\log `{=tex}n) \]

But if the tree becomes skewed:

``` text
10
  \
   20
     \
      30
        \
         40
```

it behaves like a linked list.

Then search can degrade to:

\[ O(n) \]

This is why the project uses **balanced trees**.

------------------------------------------------------------------------

# 10. BST Insertion

To insert a value:

1.  Start at the root.
2.  Compare the new value with the current node.
3.  If smaller, move left.
4.  If larger, move right.
5.  Continue until an empty position is found.
6.  Insert the new node.

Example: insert `65`.

``` text
        50
          \
           70
          /
         60
```

Since:

``` text
65 > 50
65 < 70
65 > 60
```

it becomes the right child of `60`.

------------------------------------------------------------------------

# 11. BST Deletion

Deletion has three major cases.

## Case 1 --- Leaf Node

Delete a node with no children.

``` text
     50
    /
   30
```

Delete `30`.

Result:

``` text
50
```

## Case 2 --- One Child

``` text
    50
      \
       70
         \
          80
```

Delete `70`.

`80` takes its place.

``` text
    50
      \
       80
```

## Case 3 --- Two Children

Suppose:

``` text
       50
      /  \
    30    70
         /  \
        60   80
```

Deleting `70` requires replacing it with a suitable value, commonly:

-   inorder successor, or
-   inorder predecessor.

The inorder successor is the smallest value in the right subtree.

Here it is `80` if considering the immediate structure, or `60`
depending on which node is selected. The general rule is what matters:
select the next valid BST ordering element and restructure the tree.

------------------------------------------------------------------------

# 12. Tree Traversals

Traversal means visiting all nodes in a systematic order.

The report explicitly mentions:

-   inorder
-   preorder
-   postorder

------------------------------------------------------------------------

## 12.1 Inorder Traversal

Order:

``` text
Left -> Root -> Right
```

For:

``` text
       50
      /  \
    30    70
```

the traversal is:

``` text
30 50 70
```

For a BST, inorder traversal produces sorted order.

This is one of the most important properties of BSTs.

------------------------------------------------------------------------

## 12.2 Preorder Traversal

Order:

``` text
Root -> Left -> Right
```

Example:

``` text
       50
      /  \
    30    70
```

Result:

``` text
50 30 70
```

------------------------------------------------------------------------

## 12.3 Postorder Traversal

Order:

``` text
Left -> Right -> Root
```

Result:

``` text
30 70 50
```

Postorder is useful when child information must be processed before the
parent.

------------------------------------------------------------------------

# 13. AVL Trees

An **AVL tree** is a self-balancing Binary Search Tree.

The name comes from its inventors:

-   Adelson-Velsky
-   Landis

The key property is that the tree keeps the height of left and right
subtrees sufficiently close.

The balance factor is:

\[ BF = height(left) - height(right) \]

For an AVL tree, each node must have:

\[ BF `\in `{=tex}{-1,0,+1} \]

If the balance factor becomes `+2` or `-2`, the tree needs rebalancing.

------------------------------------------------------------------------

# 14. Why AVL Trees Are Used in This Project

Patient records continuously arrive.

Records may be:

-   inserted
-   deleted
-   searched
-   updated

If a normal BST becomes skewed, operations can become `O(n)`.

AVL trees actively rebalance themselves so the height remains
logarithmic.

Therefore:

-   Search ≈ `O(log n)`
-   Insert ≈ `O(log n)`
-   Delete ≈ `O(log n)`

This matches the report's objective of keeping indexing operations
logarithmic as the record count grows.

------------------------------------------------------------------------

# 15. AVL Rotations

AVL balancing is achieved through rotations.

There are four classical imbalance patterns:

1.  LL
2.  RR
3.  LR
4.  RL

------------------------------------------------------------------------

## 15.1 LL Case

Example:

``` text
       30
      /
    20
   /
 10
```

The tree is too heavy on the left-left side.

Perform a **right rotation**.

Result:

``` text
      20
     /  \
   10    30
```

------------------------------------------------------------------------

## 15.2 RR Case

Example:

``` text
10
  \
   20
     \
      30
```

Perform a **left rotation**.

Result:

``` text
      20
     /  \
   10    30
```

------------------------------------------------------------------------

## 15.3 LR Case

Example:

``` text
      30
     /
   10
     \
      20
```

This is left-right.

Perform:

1.  left rotation on `10`
2.  right rotation on `30`

Result:

``` text
      20
     /  \
   10    30
```

------------------------------------------------------------------------

## 15.4 RL Case

Example:

``` text
10
  \
   30
   /
 20
```

Perform:

1.  right rotation on `30`
2.  left rotation on `10`

Result:

``` text
      20
     /  \
   10    30
```

------------------------------------------------------------------------

# 16. Threaded Binary Trees

A threaded binary tree uses otherwise-unused child pointers to store
traversal-related links.

Normally a node may have:

``` text
left -> child
right -> child
```

If a child is absent, the pointer is normally null.

A threaded tree can use such pointers to point toward:

-   inorder predecessor
-   inorder successor

This can make traversal possible with less dependence on recursion or an
auxiliary stack.

The report specifically mentions threaded binary trees as part of Unit
1.

It also notes that extra thread pointers create additional memory cost.

That is an important implementation trade-off:

> Faster or simpler traversal mechanisms can require additional metadata
> and therefore additional memory.

------------------------------------------------------------------------

# 17. Binary Heaps

A heap is a complete binary tree satisfying a heap-order property.

Two common forms are:

-   min-heap
-   max-heap

## Min-Heap

Parent is smaller than or equal to its children.

``` text
        5
      /   \
     8     10
    / \
   12  15
```

The minimum value is always at the root.

## Max-Heap

Parent is greater than or equal to its children.

``` text
        20
      /    \
     15     12
    /  \
   8    10
```

The maximum value is at the root.

------------------------------------------------------------------------

# 18. Heap as a Priority Queue

A priority queue removes elements according to priority rather than
arrival order.

In the outbreak system, cases may have priorities such as:

``` text
Critical
High
Medium
Low
```

A heap can efficiently maintain the next critical case.

Typical heap operations:

-   Insert: `O(log n)`
-   Extract minimum/maximum: `O(log n)`
-   Peek minimum/maximum: `O(1)`

This is why the report proposes heaps for critical-case prioritisation.

------------------------------------------------------------------------

# 19. B-Trees and B+ Trees

AVL trees are excellent for in-memory search structures.

But large datasets may be stored on disk.

Disk access is much more expensive than accessing RAM.

B-trees and B+ trees are designed to reduce the number of disk accesses
by storing many keys per node.

Instead of:

``` text
        50
       /  \
     25    75
```

a multiway tree might contain:

``` text
             [30 | 60]
           /     |      \
     many keys many keys many keys
```

Each node can contain many keys and many children.

This reduces tree height.

------------------------------------------------------------------------

# 20. B+ Trees

A B+ tree is especially useful for database-style indexing.

The internal nodes primarily guide searches.

Actual records or record pointers are stored at the leaf level.

Leaves are commonly linked:

``` text
[10 20 30] -> [40 50 60] -> [70 80 90]
```

This makes range queries efficient.

For example:

> Find all patient records whose IDs lie between 100000 and 200000.

The system can locate the first relevant leaf and then move through
linked leaves.

This is why B+ trees are a natural fit for a disk-backed record store.

------------------------------------------------------------------------

# 21. Red-Black Trees

A red-black tree is another self-balancing BST.

Each node has a colour:

``` text
red
black
```

The colouring rules constrain the height of the tree.

Unlike AVL trees, red-black trees generally allow somewhat more
imbalance but can require fewer rotations during updates.

The report places red-black trees under Unit 5.

Conceptually:

``` text
Balanced BST options:

AVL
  -> stricter balance
  -> strong lookup performance

Red-Black
  -> looser balance
  -> efficient updates
```

------------------------------------------------------------------------

# 22. Advanced Heaps

The report also includes:

-   binomial heaps
-   Fibonacci heaps

These are advanced priority-queue structures.

They are particularly relevant to graph algorithms and repeated priority
updates.

------------------------------------------------------------------------

# 23. Binomial Heap

A binomial heap is a collection of binomial trees satisfying heap-order
properties.

It supports efficient merging of heaps.

This is useful when multiple priority queues need to be combined.

The exact implementation is more complex than a binary heap, but the
central idea is:

> Build a priority queue from a structured collection of trees, allowing
> operations such as union to be performed efficiently.

------------------------------------------------------------------------

# 24. Fibonacci Heap

A Fibonacci heap is designed to make some priority-queue operations very
efficient in amortized analysis.

The operation especially relevant to Dijkstra's algorithm is:

``` text
decrease-key
```

The theoretical amortized complexity of decrease-key is:

\[ O(1) \]

while extract-min is:

\[ O(`\log `{=tex}n) \]

amortized.

This is why Fibonacci heaps sometimes appear in theoretical discussions
of shortest-path algorithms.

However, they are considerably more complicated to implement than binary
heaps.

For an academic project, the theoretical value is significant even if
the practical implementation uses a simpler structure.

------------------------------------------------------------------------

# 25. Module 2 --- Contact Network as a Graph

The project represents person-to-person contact as a **graph**.

A graph consists of:

-   vertices / nodes
-   edges

In this project:

``` text
Vertex = person / case / location
Edge = contact or movement relationship
```

Example:

``` text
A ----- B
|       |
|       |
C ----- D
```

This means:

-   A had a relationship with B
-   A had a relationship with C
-   B had a relationship with D
-   C had a relationship with D

------------------------------------------------------------------------

# 26. Why a Graph Is Appropriate

An outbreak does not simply exist as a list.

It propagates through relationships.

For example:

``` text
Person A
   |
Person B
   |
Person C
   |
Person D
```

If A and B have contact, B and C have contact, and C and D have contact,
then the network provides a way to reason about possible transmission
chains.

This is fundamentally a graph problem.

------------------------------------------------------------------------

# 27. Graph Terminology

## Vertex

A node in the graph.

## Edge

A relationship between two vertices.

## Degree

Number of edges connected to a vertex.

## Path

A sequence of connected vertices.

Example:

``` text
A -> B -> C -> D
```

## Cycle

A path that returns to the starting point.

``` text
A -> B -> C -> A
```

## Connected Component

A set of vertices where each relevant vertex is reachable from the
others through paths.

This is useful for cluster detection.

------------------------------------------------------------------------

# 28. Directed and Undirected Graphs

An **undirected graph** means:

``` text
A --- B
```

represents a relationship in both directions.

A **directed graph** means:

``` text
A ---> B
```

represents a directional relationship.

Contact networks can use either representation depending on what the
edge means.

For example:

-   physical contact may be undirected
-   movement or reported transmission direction may be directed

The project needs to define this carefully during implementation.

------------------------------------------------------------------------

# 29. Weighted Graphs

A weighted graph attaches a numerical value to each edge.

Example:

``` text
A --5-- B
```

The edge weight could represent:

-   contact duration
-   physical proximity
-   travel volume
-   estimated transmission cost
-   risk
-   another project-defined metric

The report specifically proposes using contact duration and proximity to
create weights for Dijkstra's algorithm.

------------------------------------------------------------------------

# 30. Adjacency Matrix

An adjacency matrix represents a graph using a two-dimensional array.

For four vertices:

``` text
    A B C D
A   0 1 1 0
B   1 0 0 1
C   1 0 0 1
D   0 1 1 0
```

`1` means an edge exists.

`0` means no edge exists.

For weighted graphs, the matrix can contain weights instead of 1s.

### Complexity

Space:

\[ O(V\^2) \]

This is useful for dense graphs but wasteful for sparse graphs.

------------------------------------------------------------------------

# 31. Adjacency List

An adjacency list stores neighbours for each vertex.

Example:

``` text
A -> B, C
B -> A, D
C -> A, D
D -> B, C
```

Space:

\[ O(V+E) \]

This is usually much better for sparse networks.

For a contact network, an adjacency list is often more natural because
one person may have contacts with only a small subset of the entire
population.

------------------------------------------------------------------------

# 32. BFS --- Breadth-First Search

BFS explores a graph level by level.

It uses a **queue**.

The basic idea is:

``` text
Start
  |
Visit all immediate neighbours
  |
Visit neighbours of those neighbours
  |
Continue outward
```

Example:

``` text
        A
      / | \
     B  C  D
    / \
   E   F
```

Starting from A:

``` text
A
B C D
E F
```

The BFS order is:

``` text
A, B, C, D, E, F
```

------------------------------------------------------------------------

# 33. Why BFS Fits Exposure Levels

The report proposes BFS to identify exposure levels hop by hop.

Suppose:

``` text
A = confirmed case
B, C = direct contacts
D, E = contacts of B/C
F = contact of D
```

Then:

``` text
Level 0: A
Level 1: B, C
Level 2: D, E
Level 3: F
```

These levels can be interpreted computationally as network distance.

The system must not automatically treat graph distance as biological
transmission certainty. It is a computational representation of
connectivity.

------------------------------------------------------------------------

# 34. BFS Algorithm

Pseudo-code:

``` text
BFS(graph, start):
    create queue
    mark start visited
    enqueue start

    while queue is not empty:
        current = dequeue

        for each neighbour of current:
            if neighbour is not visited:
                mark neighbour visited
                enqueue neighbour
```

The `visited` structure is not another queue.

It is normally a:

-   boolean array
-   set
-   hash set

Its purpose is to remember which vertices have already been discovered.

For adjacency lists:

\[ O(V+E) \]

------------------------------------------------------------------------

# 35. DFS --- Depth-First Search

DFS explores as deeply as possible before backtracking.

It can be implemented using:

-   recursion
-   explicit stack

Example:

``` text
A
|
B
|
C
|
D
```

DFS follows:

``` text
A -> B -> C -> D
```

before returning.

------------------------------------------------------------------------

# 36. DFS for Cluster Detection

Suppose a graph contains:

``` text
A -- B -- C

X -- Y

P -- Q -- R
```

There are three connected components.

DFS can start at A and mark:

``` text
A, B, C
```

Then find an unvisited vertex X:

``` text
X, Y
```

Then:

``` text
P, Q, R
```

Thus DFS can identify connected clusters.

------------------------------------------------------------------------

# 37. DFS Using Recursion

Conceptually:

``` text
DFS(node):
    mark node visited

    for each neighbour:
        if neighbour not visited:
            DFS(neighbour)
```

The function call stack acts as the stack.

------------------------------------------------------------------------

# 38. DFS Using an Explicit Stack

``` text
push(start)

while stack not empty:
    node = pop()

    if node not visited:
        mark visited

        for neighbour:
            push(neighbour)
```

Both methods implement depth-first exploration.

Complexity with an adjacency list:

\[ O(V+E) \]

------------------------------------------------------------------------

# 39. Dijkstra's Algorithm

Dijkstra's algorithm finds shortest paths from one source to all
reachable vertices in a graph with non-negative edge weights.

Example:

``` text
A --2-- B
|       |
5       1
|       |
C --2-- D
```

Starting from A:

-   distance(A) = 0
-   distance(B) = 2
-   distance(C) = 5 initially
-   via B, D becomes 3
-   via D, C becomes 5

The algorithm continually selects the currently closest unprocessed
vertex and relaxes its edges.

------------------------------------------------------------------------

# 40. Relaxation

Suppose:

``` text
dist[A] = 0
A --5-- B
```

Then:

``` text
candidate = dist[A] + 5
          = 5
```

If:

``` text
5 < dist[B]
```

update:

``` text
dist[B] = 5
```

This operation is called **relaxation**.

------------------------------------------------------------------------

# 41. Dijkstra in the Project

The project proposes weights based on:

-   contact duration
-   proximity

The objective is to estimate a computationally preferred or most
plausible transmission route.

Important distinction:

> Dijkstra finds the shortest path according to the numerical
> edge-weight model. It does not independently prove that the biological
> transmission actually occurred along that path.

The quality of the output therefore depends heavily on how the edge
weights are defined.

------------------------------------------------------------------------

# 42. Dijkstra Complexity

With a binary heap and adjacency list:

\[ O((V+E)`\log `{=tex}V) \]

Often simplified to:

\[ O(E`\log `{=tex}V) \]

for connected sparse graphs.

This is the complexity estimate given in the report.

------------------------------------------------------------------------

# 43. Bellman-Ford

Bellman-Ford also computes shortest paths from a source.

Its major advantage is that it can handle **negative edge weights**.

It can also detect reachable negative cycles.

Basic complexity:

\[ O(VE) \]

For this project, Dijkstra is more directly aligned with non-negative
contact-related weights, while Bellman-Ford is part of the syllabus and
provides an important comparison.

------------------------------------------------------------------------

# 44. Floyd-Warshall

Floyd-Warshall computes shortest paths between **all pairs** of
vertices.

Its recurrence is based on whether allowing an intermediate vertex `k`
improves the path from `i` to `j`.

Conceptually:

\[ D\[i\]\[j\] = `\min`{=tex}(D\[i\]\[j\], D\[i\]\[k\]+D\[k\]\[j\]) \]

Its time complexity is:

\[ O(V\^3) \]

This becomes extremely expensive as `V` becomes large.

The report explicitly identifies this as a challenge.

For a large national contact graph, all-pairs Floyd-Warshall may be
impractical.

A possible design response is to:

-   restrict analysis to a district-level subgraph, or
-   use repeated single-source shortest-path computations where
    appropriate.

------------------------------------------------------------------------

# 45. Minimum Spanning Tree

A Minimum Spanning Tree (MST) connects all vertices of a connected
weighted undirected graph with minimum total edge weight.

It contains:

\[ V-1 \]

edges.

It does not contain cycles.

The project includes:

-   Prim's algorithm
-   Kruskal's algorithm

------------------------------------------------------------------------

# 46. Prim's Algorithm

Prim's algorithm grows an MST from a starting vertex.

At each stage, it selects the cheapest edge that connects the current
tree to an unvisited vertex.

Conceptually:

``` text
Start A
 |
choose cheapest outgoing edge
 |
expand
 |
choose next cheapest valid edge
 |
continue
```

------------------------------------------------------------------------

# 47. Kruskal's Algorithm

Kruskal's algorithm:

1.  Sort all edges by weight.
2.  Consider edges from smallest to largest.
3.  Add an edge if it does not create a cycle.
4.  Stop after `V-1` edges.

A **Disjoint Set Union (DSU)** structure is commonly used to efficiently
detect whether adding an edge would create a cycle.

The project plans to implement Kruskal's algorithm after constructing
the contact graph.

------------------------------------------------------------------------

# 48. Transitive Closure

Transitive closure answers reachability questions.

For example:

``` text
A -> B
B -> C
```

Then:

``` text
A can reach C
```

even though there is no direct A-C edge.

A common implementation uses the Floyd-Warshall-style Warshall
algorithm.

The result answers questions such as:

> Is there any path from location/person A to location/person B?

This is different from shortest-path computation.

------------------------------------------------------------------------

# 49. DAGs

A **Directed Acyclic Graph (DAG)** is a directed graph with no directed
cycles.

Example:

``` text
A -> B -> D
 \-> C -> D
```

There is no way to follow arrows and return to A.

DAGs are useful for:

-   dependency relationships
-   scheduling
-   staged processes
-   dynamic programming

The project lists DAGs as part of the graph syllabus even though the
primary outbreak-network model is not necessarily a DAG.

------------------------------------------------------------------------

# 50. Module 3 --- Dynamic Programming

Dynamic Programming (DP) is used when a problem has:

1.  **Overlapping subproblems**
2.  **Optimal substructure**

The project uses DP primarily for resource allocation.

------------------------------------------------------------------------

# 51. Optimal Substructure

A problem has optimal substructure when an optimal solution can be
constructed from optimal solutions to smaller subproblems.

Example:

If the best allocation for a capacity of 10 contains an item selection
that itself represents the best allocation for a smaller capacity/state,
DP can reuse that result.

------------------------------------------------------------------------

# 52. Overlapping Subproblems

Suppose recursive computation repeatedly solves:

``` text
F(5)
F(4)
F(3)
F(2)
...
```

and the same subproblems appear repeatedly.

Instead of recomputing them, DP stores the answers.

Two common methods:

-   memoization
-   tabulation

------------------------------------------------------------------------

# 53. Memoization

Memoization is top-down.

``` text
solve(state):
    if state already computed:
        return stored answer

    calculate answer
    store answer
    return answer
```

------------------------------------------------------------------------

# 54. Tabulation

Tabulation is bottom-up.

Start with small known states:

``` text
dp[0]
dp[1]
dp[2]
...
```

and build toward the final state.

------------------------------------------------------------------------

# 55. 0/1 Knapsack

The report models resource allocation as a **0/1 knapsack variant**.

The basic problem:

Given items with:

-   weight/cost
-   value

and a capacity limit, choose items so total value is maximised without
exceeding capacity.

Each item can be selected:

``` text
0 times or 1 time
```

Hence:

**0/1 Knapsack**

------------------------------------------------------------------------

# 56. Mapping Knapsack to Medical Supplies

The project proposes:

``` text
weight = resource cost
value = expected cases averted
capacity = available budget/supply
```

For example:

  Centre     Cost   Expected benefit
  -------- ------ ------------------
  A             5                 12
  B             4                  9
  C             7                 15
  D             3                  7

If only a limited amount is available, the system must determine which
combination gives the maximum modeled benefit.

The output is therefore computed rather than simply guessed.

------------------------------------------------------------------------

# 57. 0/1 Knapsack Recurrence

Let:

\[ dp\[i\]\[w\] \]

represent the maximum value obtainable using the first `i` items with
capacity `w`.

For item `i`:

If its weight exceeds `w`:

\[ dp\[i\]\[w\] = dp\[i-1\]\[w\] \]

Otherwise:

\[ dp\[i\]\[w\] = `\max`{=tex}( dp\[i-1\]\[w\], value_i +
dp\[i-1\]\[w-weight_i\] ) \]

The two choices are:

1.  Do not take the item.
2.  Take the item.

------------------------------------------------------------------------

# 58. Knapsack Complexity

For `n` items and capacity `W`:

Time:

\[ O(nW) \]

Space in the straightforward 2D version:

\[ O(nW) \]

Space can sometimes be reduced to:

\[ O(W) \]

using a one-dimensional DP array.

The report explicitly estimates:

\[ O(nW) \]

for the knapsack formulation.

------------------------------------------------------------------------

# 59. Why Greedy Is Not Automatically Correct

The report says the DP result will be compared with a naive greedy
split.

A greedy approach might select the centre with the largest:

``` text
benefit / cost
```

ratio.

That can be useful heuristically, but it is not guaranteed to solve
every 0/1 knapsack instance optimally.

Dynamic programming is used because it systematically evaluates the
relevant states.

------------------------------------------------------------------------

# 60. Longest Common Subsequence

The report applies LCS to comparing outbreak timelines across districts.

The **Longest Common Subsequence** finds the longest sequence appearing
in two sequences in the same order, without requiring the elements to be
contiguous.

Example:

``` text
A = A B C D E
B = A C E
```

The LCS is:

``` text
A C E
```

------------------------------------------------------------------------

# 61. LCS Recurrence

Let:

\[ L\[i\]\[j\] \]

be the LCS length for prefixes of two sequences.

If the current elements match:

\[ L\[i\]\[j\] = 1 + L\[i-1\]\[j-1\] \]

Otherwise:

\[ L\[i\]\[j\] = `\max`{=tex}(L\[i-1\]\[j\], L\[i\]\[j-1\]) \]

This is another classic DP problem.

------------------------------------------------------------------------

# 62. Why LCS Can Help Compare Timelines

Suppose district A has an event sequence:

``` text
Cases -> Hospitalisation -> Peak -> Recovery
```

District B:

``` text
Cases -> Testing -> Hospitalisation -> Peak -> Recovery
```

The common sequence can reveal structural similarity.

However, LCS measures **sequence similarity**, not epidemiological
causality.

It should therefore be interpreted as a computational comparison tool.

------------------------------------------------------------------------

# 63. Matrix Chain Multiplication

Matrix Chain Multiplication is another DP problem listed in the report.

Suppose we need to multiply:

``` text
A × B × C
```

The order of multiplication matters computationally.

Because matrix multiplication is associative:

``` text
(A × B) × C
```

and:

``` text
A × (B × C)
```

produce the same mathematical result, but they may require different
numbers of scalar multiplications.

DP finds the cheapest parenthesisation.

------------------------------------------------------------------------

# 64. Resource Allocation

Resource allocation is a broader optimisation concept.

The project applies it to:

-   vaccines
-   test kits
-   oxygen
-   healthcare resources

The essential computational question is:

> Given finite resources and multiple competing destinations, how can
> resources be distributed according to a defined objective?

A real system would need carefully validated objectives and constraints.
In the academic project, expected cases averted is used as the value
function.

------------------------------------------------------------------------

# 65. Module 4 --- Backtracking

Backtracking systematically explores possible solutions and abandons a
partial solution when it cannot lead to a valid complete solution.

General structure:

``` text
Choose
  |
Check
  |
Continue
  |
If invalid -> backtrack
```

It is essentially structured search through a solution space.

------------------------------------------------------------------------

# 66. Example of Backtracking

Suppose we must choose a sequence of decisions:

``` text
A
B
C
```

We may explore:

``` text
A
├── B
│   ├── C
│   └── ...
└── ...
```

If a partial choice violates a constraint:

``` text
A -> B -> invalid
```

we stop exploring that branch and return to an earlier decision.

This avoids exploring every possible continuation.

------------------------------------------------------------------------

# 67. Graph Colouring

Graph colouring assigns colours to vertices so adjacent vertices do not
receive the same colour.

Example:

``` text
A ----- B
|       |
|       |
C ----- D
```

Possible colouring:

``` text
A = Red
B = Blue
C = Blue
D = Red
```

Adjacent vertices have different colours.

------------------------------------------------------------------------

# 68. Graph Colouring for District Zoning

The project proposes graph colouring for zoning neighbouring districts.

Imagine:

``` text
District A --- District B
      |              |
District C --- District D
```

If adjacent districts cannot share the same containment policy, colours
can represent:

-   quarantine category
-   intervention level
-   testing policy
-   operational zone

The exact semantic meaning of a colour must be defined by the
implementation.

The algorithmic constraint is:

> Adjacent districts must not receive conflicting/same-category
> assignments where the model requires separation.

------------------------------------------------------------------------

# 69. N-Queens

N-Queens is a classic backtracking problem.

Place `N` queens on an `N × N` chessboard so that no two queens attack
one another.

Constraints:

-   no same row
-   no same column
-   no same diagonal

It is primarily a syllabus concept in this project rather than a direct
outbreak-monitoring feature.

It demonstrates constraint satisfaction and backtracking.

------------------------------------------------------------------------

# 70. Hamiltonian Cycle

A Hamiltonian cycle is a cycle that visits every vertex exactly once and
returns to the starting vertex.

Example:

``` text
A -> B -> C -> D -> A
```

if all vertices are visited once.

This is different from an Eulerian cycle, which is based on edges rather
than vertices.

------------------------------------------------------------------------

# 71. Travelling Salesperson Problem

The TSP asks:

> What is the minimum-cost route that visits every required location and
> returns to the starting point?

For a collection vehicle:

``` text
Depot -> Hospital A -> Hospital B -> Lab -> Hospital C -> Depot
```

we want to minimise travel cost.

The project uses a TSP-style formulation for sample collection.

------------------------------------------------------------------------

# 72. Why TSP Is Difficult

The number of possible tours grows extremely quickly.

For `n` cities, the number of possible tours is roughly factorial in
`n`.

A brute-force approach becomes impractical quickly.

That is why branch-and-bound is introduced.

------------------------------------------------------------------------

# 73. Branch-and-Bound

Branch-and-bound explores a solution space but calculates bounds to
determine whether a partial solution can still beat the best known
solution.

Two ideas:

### Branch

Split the problem into alternatives.

### Bound

Calculate a lower or upper estimate of what is achievable from that
branch.

If a branch cannot possibly improve the current best solution, prune it.

------------------------------------------------------------------------

# 74. Example of Branch-and-Bound Logic

Suppose the best route found so far costs:

``` text
100
```

A partial route has:

``` text
current cost = 80
```

A lower-bound estimate says the remaining travel must cost at least:

``` text
30
```

Therefore:

``` text
minimum possible final cost >= 110
```

Since `110` cannot beat the current best `100`, the branch can be
discarded.

This is called **pruning**.

------------------------------------------------------------------------

# 75. Difference Between Backtracking and Branch-and-Bound

Both explore solution spaces.

But their emphasis differs.

### Backtracking

Primarily asks:

> Can this partial solution still become valid?

If no:

``` text
prune
```

### Branch-and-Bound

Primarily asks:

> Can this partial solution possibly become better than the best
> solution found so far?

If no:

``` text
prune
```

So branch-and-bound uses optimisation bounds.

------------------------------------------------------------------------

# 76. Why Branch-and-Bound Is a Challenge in This Project

The report states that quarantine scheduling can grow explosively as
constraints become tighter.

The difficult part is constructing a bounding function that is:

-   strong enough to prune many branches
-   safe enough not to accidentally discard valid optimal solutions

A weak bound causes too much search.

An incorrect bound can produce wrong results.

------------------------------------------------------------------------

# 77. Unit 1 --- Complete Concept Map

Unit 1 contains:

-   Binary trees
-   Tree traversals
-   BST
-   BST insertion
-   BST deletion
-   BST search
-   Binary heaps
-   Threaded binary trees
-   AVL trees

Project mapping:

``` text
Patient records
      |
AVL / BST-style indexing

Critical cases
      |
Heap / priority queue
```

The most important connection is that trees solve **hierarchical and
ordered lookup**, while heaps solve **priority ordering**.

------------------------------------------------------------------------

# 78. Unit 2 --- Complete Concept Map

Unit 2 contains:

-   adjacency matrix
-   adjacency list
-   DFS
-   BFS
-   Prim's algorithm
-   Kruskal's algorithm
-   DAGs
-   transitive closure
-   Dijkstra
-   Bellman-Ford
-   Floyd-Warshall

Project mapping:

``` text
Contact network
      |
      +-- BFS -> exposure levels
      |
      +-- DFS -> clusters
      |
      +-- Dijkstra -> weighted paths
      |
      +-- MST -> connectivity/cost analysis
      |
      +-- closure -> reachability
```

------------------------------------------------------------------------

# 79. Unit 3 --- Complete Concept Map

Unit 3 contains:

-   0/1 knapsack
-   LCS
-   matrix chain multiplication
-   resource allocation

Project mapping:

``` text
Medical supply allocation
        |
        +-- 0/1 Knapsack

District timeline comparison
        |
        +-- LCS

Multi-stage computational optimisation
        |
        +-- DP concepts
```

The main theme is:

> Store and reuse solutions to smaller subproblems.

------------------------------------------------------------------------

# 80. Unit 4 --- Complete Concept Map

Unit 4 contains:

-   Backtracking
-   Branch-and-Bound
-   TSP
-   Graph colouring
-   N-Queens
-   Hamiltonian cycles
-   Sum of subsets

Project mapping:

``` text
District zoning
      |
Graph colouring

Collection routing
      |
TSP + Branch-and-Bound

Constraint-based scheduling
      |
Backtracking
```

------------------------------------------------------------------------

# 81. Unit 5 --- Complete Concept Map

Unit 5 contains:

-   Red-black trees
-   B-trees
-   B+ trees
-   Binomial heaps
-   Fibonacci heaps

Project mapping:

``` text
Disk-backed record store
       |
B-tree / B+ tree

Advanced priority operations
       |
Binomial / Fibonacci heap

Alternative balanced indexing
       |
Red-black tree
```

------------------------------------------------------------------------

# 82. Complexity Analysis

The report's complexity analysis is essential because the project is a
DSA project.

A correct solution is not enough.

We also need to understand how its cost changes with input size.

------------------------------------------------------------------------

## 82.1 Big-O Notation

Big-O describes how an algorithm's resource usage grows as input size
increases.

Common complexities:

``` text
O(1)
O(log n)
O(n)
O(n log n)
O(n²)
O(n³)
O(2ⁿ)
O(n!)
```

Generally, lower growth is preferable for large inputs, although actual
performance also depends on constants, memory access, implementation
details and input structure.

------------------------------------------------------------------------

# 83. O(1)

Constant time.

Example:

``` text
array[index]
```

If the array supports direct indexing, accessing one element does not
require scanning the whole array.

------------------------------------------------------------------------

# 84. O(log n)

Logarithmic time.

Typical example:

-   balanced BST search

Each decision eliminates a substantial part of the search space.

For a balanced binary tree, height is approximately:

\[ `\log`{=tex}\_2 n \]

------------------------------------------------------------------------

# 85. O(n)

Linear time.

Example:

``` text
scan every patient record
```

If the dataset doubles, the approximate work doubles.

------------------------------------------------------------------------

# 86. O(n log n)

Common in efficient sorting algorithms.

Also appears in several graph algorithms.

For Dijkstra with a heap, the report uses:

\[ O(E`\log `{=tex}V) \]

------------------------------------------------------------------------

# 87. O(n²)

Quadratic time.

If `n` doubles:

\[ n\^2 `\rightarrow `{=tex}(2n)\^2 = 4n\^2 \]

The work becomes roughly four times larger.

------------------------------------------------------------------------

# 88. O(n³)

Floyd-Warshall has:

\[ O(V\^3) \]

If the number of vertices doubles:

\[ (2V)\^3 = 8V\^3 \]

This explains why all-pairs algorithms can become problematic for very
large graphs.

------------------------------------------------------------------------

# 89. O(nW)

The 0/1 knapsack DP has:

\[ O(nW) \]

where:

-   `n` = number of items
-   `W` = capacity

This is called **pseudo-polynomial** complexity because it depends on
the numerical value of the capacity rather than simply the number of
bits needed to represent it.

------------------------------------------------------------------------

# 90. O(2ⁿ)

Exponential.

The number of possibilities can double as `n` increases by one.

Backtracking problems may exhibit exponential worst-case behaviour.

------------------------------------------------------------------------

# 91. O(n!)

Factorial.

TSP brute-force search is a classic example.

For `n` destinations, permutations grow extremely rapidly.

This is why pruning strategies matter.

------------------------------------------------------------------------

# 92. The Project's Main Complexity Targets

The report identifies:

### Indexing

\[ O(`\log `{=tex}n) \]

### Dijkstra

\[ O(E`\log `{=tex}V) \]

### Knapsack

\[ O(nW) \]

These estimates are intended to establish feasibility before coding
begins.

Later benchmarking will compare actual runtime against these theoretical
expectations.

------------------------------------------------------------------------

# 93. Data Model

A data model defines what the system actually stores.

The report says the project has defined:

-   what a node represents
-   what an edge represents
-   what an edge weight represents
-   which patient attributes are used as tree keys

A conceptual patient record might contain:

``` text
Patient
---------
patient_id
name
age
location
diagnosis
case_status
report_date
```

A graph edge might conceptually contain:

``` text
Contact
---------
source
destination
duration
proximity
weight
timestamp
```

The exact final schema must be determined by the implementation.

------------------------------------------------------------------------

# 94. What a Node Means

There can be multiple layers of nodes.

### Person-level graph

``` text
Node = individual patient/person
```

### Location-level graph

``` text
Node = district / hospital / ward
```

### Case-level graph

``` text
Node = confirmed case
```

The report refers to patient and location records and person-to-person
contact.

A robust implementation should clearly distinguish these layers rather
than mixing them without definition.

------------------------------------------------------------------------

# 95. What an Edge Means

An edge represents a relationship.

For person-to-person contact:

``` text
Person A ---- Person B
```

could mean:

> A and B had a recorded contact event.

The system must define whether repeated contacts:

-   create multiple edges,
-   update one aggregate edge,
-   or become timestamped events.

This is an implementation decision.

------------------------------------------------------------------------

# 96. What an Edge Weight Means

The report proposes deriving weights from:

-   contact duration
-   proximity

For example, a simplified model might conceptually be:

``` text
risk-related weight = f(duration, proximity)
```

However, the mathematical formula is not specified in the report.

Therefore, it should not be invented and presented as an existing
project requirement.

The next implementation stage should define and justify it.

------------------------------------------------------------------------

# 97. Handling Real Surveillance Data

One of the report's important observations is that real surveillance
data is:

-   incomplete
-   delayed
-   potentially biased
-   sometimes received out of order

This matters because algorithms normally assume clean input.

Suppose contacts arrive in this order:

``` text
Day 3 contact
Day 1 contact
Day 2 contact
```

The system must decide how historical updates affect:

-   graph structure
-   weights
-   clusters
-   shortest paths
-   timeline analysis

This is a data-engineering issue as much as an algorithmic issue.

------------------------------------------------------------------------

# 98. Why Out-of-Order Data Is Difficult

Suppose a path is:

``` text
A -> B -> C
```

and the system first receives:

``` text
A -> B
B -> C
```

Then later receives an earlier contact:

``` text
A -> X
```

The new edge may change:

-   cluster structure
-   shortest paths
-   risk calculations
-   downstream recommendations

Therefore, the system needs a strategy for updating derived information.

------------------------------------------------------------------------

# 99. Real Data vs Academic Data

The report identifies:

-   WHO Global Health Observatory / WHO Data Hub
-   Johns Hopkins CSSE COVID-19 Data Repository
-   human mobility datasets
-   published forecasting work

The role of these sources is validation and realistic testing.

They do not automatically prove that the proposed system's predictions
are medically correct.

------------------------------------------------------------------------

# 100. WHO Data

The report identifies WHO Global Health Observatory / WHO Data Hub as a
reference for:

-   standardised reporting
-   record schema
-   sanity checking case counts

A schema reference answers:

> What fields and structures should our data contain?

A sanity check asks:

> Does our processed data produce values that are broadly consistent
> with the reference data?

------------------------------------------------------------------------

# 101. Johns Hopkins CSSE Dataset

The report identifies the Johns Hopkins CSSE COVID-19 repository as the
main test input for:

-   graph-related experiments
-   forecasting modules
-   stressing data structures

The reason given is that the data is:

-   public
-   regional
-   time-series based
-   sufficiently large for testing

------------------------------------------------------------------------

# 102. Forecasting Benchmark

The report cites:

> Ribeiro, da Silva, Mariani & dos Santos Coelho (2020)

as a source containing error figures for short-horizon forecasting
methods.

The project's intended use is comparative:

``` text
Our forecasting approach
        vs.
published benchmark
```

This provides a reference point for evaluation.

------------------------------------------------------------------------

# 103. Human Mobility Data

The report cites Kraemer et al. (2020) to support the use of aggregated
movement information.

Movement between regions can be represented computationally as edges.

Example:

``` text
District A ---- District B
       travel volume = 5000
```

The number can contribute to an edge-weighting model.

Again, the exact formula must be specified by the implementation.

------------------------------------------------------------------------

# 104. Contact-Timing Data

The report cites Chaintreau et al. (2007) as a source for realistic
inter-contact timing distributions.

This is useful for testing.

Instead of generating completely artificial random contact intervals,
the project can test algorithms against distributions inspired by
observed mobility/contact behaviour.

------------------------------------------------------------------------

# 105. Literature Review --- Why Each Source Matters

The report uses five theoretical sources.

## Cormen, Leiserson, Rivest & Stein

Used for:

-   algorithmic complexity
-   standard algorithm formulations
-   trees
-   graphs
-   dynamic programming

It forms the general DSA foundation.

## Keeling & Eames

Used to justify:

> Transmission is better represented as a contact network than as simple
> uniform mixing.

This supports the graph representation.

## Bajardi et al.

Used to support:

> Movement between regions can influence disease spread.

This supports inter-district weighted edges.

## Bansal et al.

Provides an important caution concerning:

-   data volume
-   bias
-   validation
-   surveillance-data problems

This prevents the system from treating large datasets as automatically
reliable.

## Vespignani

Used to understand computational cost in spreading processes on large
networks.

This helps set realistic expectations about scale.

------------------------------------------------------------------------

# 106. Why the Literature Review Is More Than a Bibliography

The report does not merely list papers.

Each source is mapped to a design decision.

``` text
Source
  |
  v
Finding
  |
  v
Design implication
```

Examples:

``` text
Network epidemiology
      |
contact relationships matter
      |
use graph

Mobility research
      |
movement matters
      |
weighted regional edges

Big-data surveillance
      |
data is incomplete/biased
      |
validation and data handling matter
```

This is the stronger way to explain the literature review in a viva.

------------------------------------------------------------------------

# 107. Target Users

The report identifies two major stakeholder categories.

## Public Health Epidemiologists

They need to:

-   understand how infection is moving
-   identify connected cases
-   investigate clusters
-   examine relationships between locations

## Healthcare Logistics Managers / District Health Officers

They need to:

-   allocate finite supplies
-   prioritise interventions
-   make resource decisions
-   compare alternative allocations

The project therefore has both:

``` text
network-analysis functionality
```

and:

``` text
optimisation functionality
```

------------------------------------------------------------------------

# 108. Why Stakeholders Matter Technically

A technical system should not only answer:

> Can the algorithm run?

It should also answer:

> What question does the algorithm answer for the user?

For example:

  Stakeholder question                                   Algorithm
  ------------------------------------------------------ -----------------
  Who is connected to this case?                         BFS / DFS
  How many hops away?                                    BFS
  What weighted route exists?                            Dijkstra
  Which cluster is connected?                            DFS
  How should limited stock be distributed?               DP
  How should locations be zoned?                         Graph colouring
  What collection route minimises modeled travel cost?   TSP / B&B

This mapping is one of the strongest parts of the project's conceptual
design.

------------------------------------------------------------------------

# 109. Month 1 Work Completed

According to the report, Month 1 completed:

1.  System scoping
2.  Four-module breakdown
3.  Unit mapping
4.  Literature review
5.  Data-model definition
6.  Complexity analysis
7.  Repository setup

The reported progress is:

\[ 25% \]

The report explicitly says implementation and benchmarking remain the
bulk of the work.

------------------------------------------------------------------------

# 110. What "25% Complete" Means

The 25% figure should not be interpreted as:

> 25% of all code is finished.

It represents the project's stated progress in terms of:

-   scoping
-   conceptual design
-   research
-   complexity analysis
-   repository setup

The implementation is still ahead.

------------------------------------------------------------------------

# 111. Challenges Already Identified

The report lists four major challenges.

## 1. Threaded Trees and AVL Rotations

Pointer manipulation is difficult.

AVL rotation requires careful updates to:

-   child pointers
-   parent relationships if used
-   heights
-   root references

Threaded trees add additional pointer bookkeeping.

------------------------------------------------------------------------

## 2. Floyd-Warshall Scalability

Floyd-Warshall is:

\[ O(V\^3) \]

Large graphs make this expensive.

The report proposes:

-   district-level subgraphs
-   repeated Dijkstra runs

as possible alternatives.

------------------------------------------------------------------------

## 3. Branch-and-Bound Explosion

The search space can become extremely large.

The main unresolved issue is a sufficiently strong bounding function.

------------------------------------------------------------------------

## 4. Late and Incomplete Data

Real-world data may arrive:

-   late
-   missing
-   out of order

The data structure must therefore support updates without producing
inconsistent derived results.

------------------------------------------------------------------------

# 112. Repository and Implementation Structure

The report says the project repository has:

-   module structure
-   data-model notes
-   committed code

A sensible conceptual code structure could be:

``` text
project/
│
├── indexing/
│   ├── avl/
│   ├── btree/
│   └── heap/
│
├── graph/
│   ├── graph_model/
│   ├── bfs/
│   ├── dfs/
│   ├── dijkstra/
│   ├── prim/
│   ├── kruskal/
│   └── closure/
│
├── optimization/
│   ├── knapsack/
│   ├── lcs/
│   └── resource_allocation/
│
├── scheduling/
│   ├── coloring/
│   ├── backtracking/
│   └── branch_bound/
│
├── data/
│
├── benchmarks/
│
└── README
```

This is a conceptual organisation, not a statement that the existing
repository currently has exactly these directories.

------------------------------------------------------------------------

# 113. How the Whole System Connects

The four modules should not be thought of as unrelated algorithms.

A conceptual data flow is:

``` text
Raw surveillance data
        |
        v
Data ingestion
        |
        +----------------------+
        |                      |
        v                      v
Patient records          Contact events
        |                      |
        v                      v
AVL / B+ indexing       Contact graph
        |                      |
        |                +-----+-----+
        |                |     |     |
        |               BFS   DFS Dijkstra
        |                |     |     |
        |                +-----+-----+
        |                      |
        +----------+-----------+
                   |
                   v
           Decision information
                   |
          +--------+---------+
          |                  |
          v                  v
    Resource allocation   Scheduling
          |                  |
          v                  v
      Knapsack          Colouring / TSP
```

The important academic point is that each DSA technique is attached to a
distinct computational requirement.

------------------------------------------------------------------------

# 114. A Full Example

Consider a simplified outbreak.

Patients:

``` text
P1
P2
P3
P4
P5
```

Contacts:

``` text
P1 -- P2
P1 -- P3
P2 -- P4
P3 -- P5
```

Graph:

``` text
        P1
       /  \
     P2    P3
     |      |
     P4     P5
```

If P1 is a confirmed case:

### BFS

Level 0:

``` text
P1
```

Level 1:

``` text
P2, P3
```

Level 2:

``` text
P4, P5
```

### DFS

Could identify all five as one connected component.

### Dijkstra

If edges have weights:

``` text
P1-P2 = 2
P1-P3 = 5
P2-P4 = 1
P3-P5 = 2
```

then shortest weighted distances can be calculated.

------------------------------------------------------------------------

# 115. Adding Patient Indexing

Suppose patients are stored in an AVL tree by patient ID:

``` text
          250
        /     \
      120      400
     /  \      / \
   50   180  300 500
```

A query for patient `300` does not need to scan every patient.

It follows:

``` text
250
 -> right
400
 -> left
300
```

This gives efficient lookup.

------------------------------------------------------------------------

# 116. Adding Priority

Suppose critical cases have priority:

``` text
P4 = 90
P1 = 80
P3 = 70
P2 = 40
P5 = 20
```

A max-heap can maintain:

``` text
        P4:90
       /     \
   P1:80     P3:70
   /  \
 P2:40 P5:20
```

The system can retrieve the highest-priority case efficiently.

------------------------------------------------------------------------

# 117. Adding Resource Allocation

Suppose there are three healthcare centres.

``` text
Centre A: cost 5, benefit 12
Centre B: cost 4, benefit 9
Centre C: cost 7, benefit 15
```

Budget:

``` text
9
```

Possible choices:

``` text
A + B = cost 9, benefit 21
A = 5, benefit 12
B = 4, benefit 9
C = 7, benefit 15
```

The DP algorithm can identify the best feasible combination under the
defined model.

------------------------------------------------------------------------

# 118. Adding Scheduling

Suppose collection teams need to visit:

``` text
Hospital A
Hospital B
Hospital C
Laboratory D
```

There are multiple possible orders.

TSP models the route.

Branch-and-bound avoids exploring routes that cannot beat the current
best route.

------------------------------------------------------------------------

# 119. What the "AI" Part Means

The title contains "AI-Based", but the report's core is explicitly a
**data-structure and algorithm design problem**.

The listed techniques are mostly classical algorithms.

Therefore, it is important not to falsely claim that:

``` text
AVL = AI
Dijkstra = AI
Knapsack = AI
```

They are not.

A more accurate conceptual architecture is:

``` text
AI / predictive component
          |
          v
decision-support inputs
          |
          v
DSA algorithms
          |
          v
optimised monitoring / allocation
```

The report itself concentrates primarily on the DSA layer.

If a machine-learning forecasting component is added, it should be
separately defined and evaluated.

------------------------------------------------------------------------

# 120. Important Distinction: Prediction vs Optimisation

These are different tasks.

## Prediction

Question:

> What might happen?

Example:

``` text
Expected cases next week
```

## Optimisation

Question:

> Given constraints, what should we choose?

Example:

``` text
Which centres should receive limited test kits?
```

## Graph analysis

Question:

> How are entities connected?

Example:

``` text
Which cases form a connected cluster?
```

The project contains all three styles of computation.

------------------------------------------------------------------------

# 121. Important Distinction: Shortest Path vs Most Likely Transmission

Dijkstra mathematically finds:

\[ `\text{minimum total edge weight}`{=tex} \]

It does not inherently know what "most likely transmission" means.

To use it for transmission-path estimation, the project needs a
carefully defined mapping:

``` text
contact characteristics
       |
       v
edge-weight function
       |
       v
Dijkstra
       |
       v
lowest-cost path
```

The interpretation depends on the weight function.

This should be explained clearly in a viva.

------------------------------------------------------------------------

# 122. Important Distinction: Graph Distance vs Infection Distance

If BFS says:

``` text
P1 -> P2 -> P3
```

then P3 is two hops away.

That does **not** mean:

> P3 definitely became infected through P1.

It only means:

> There is a two-edge path in the recorded contact graph.

This distinction is important because a data structure describes
recorded relationships; it does not independently establish medical
causation.

------------------------------------------------------------------------

# 123. Important Distinction: Algorithmic Optimality vs Real-World Optimality

If DP produces an optimal solution, it means:

> Optimal according to the mathematical objective and constraints
> provided to the algorithm.

It does not automatically mean:

> Best real-world public-health decision.

For example, if "value" is defined only as expected cases averted, other
considerations may be missing:

-   equity
-   accessibility
-   staffing
-   storage
-   political/legal constraints
-   uncertainty
-   emergency requirements

The academic system can still demonstrate optimisation, but the model
assumptions must be explicit.

------------------------------------------------------------------------

# 124. Benchmarking

The next stage should compare theoretical complexity with measured
performance.

For example:

    Input size   AVL search   Dijkstra   Knapsack
  ------------ ------------ ---------- ----------
         1,000      measure    measure    measure
         5,000      measure    measure    measure
        10,000      measure    measure    measure
        50,000      measure    measure    measure

The point is not merely to collect numbers.

The goal is to see whether observed growth resembles theoretical growth.

------------------------------------------------------------------------

# 125. What a Good Benchmark Should Record

For each algorithm:

-   input size
-   number of vertices
-   number of edges
-   dataset characteristics
-   runtime
-   memory usage where practical
-   number of operations where meaningful
-   hardware/software environment
-   repeated trials
-   average runtime

For fair comparison, use consistent conditions.

------------------------------------------------------------------------

# 126. Example Benchmark Questions

For AVL:

> Does search remain approximately logarithmic as records increase?

For BFS:

> How does runtime grow as vertices and edges increase?

For Dijkstra:

> Does runtime behave consistently with `O(E log V)`?

For Floyd-Warshall:

> At what graph size does `O(V³)` become impractical?

For knapsack:

> How does runtime change as `n` and `W` increase?

For branch-and-bound:

> How effective is the pruning bound?

------------------------------------------------------------------------

# 127. Testing AVL Trees

AVL testing should cover:

### Normal insertion

``` text
10, 20, 30
```

Should trigger RR balancing.

### Reverse insertion

``` text
30, 20, 10
```

Should trigger LL balancing.

### Zig-zag insertion

``` text
30, 10, 20
```

Should trigger LR balancing.

### Other zig-zag

``` text
10, 30, 20
```

Should trigger RL balancing.

Also test:

-   deletion
-   duplicate keys
-   missing keys
-   root deletion
-   empty tree

------------------------------------------------------------------------

# 128. Testing Graph Algorithms

Test:

-   empty graph
-   one vertex
-   disconnected graph
-   cycle
-   self-loop if supported
-   duplicate edges if possible
-   weighted edges
-   large sparse graph
-   large dense graph

For BFS and DFS, verify the visited set prevents repeated traversal.

------------------------------------------------------------------------

# 129. Testing Dijkstra

Important tests:

1.  Simple graph
2.  Multiple possible paths
3.  Disconnected vertex
4.  Zero-weight edge if allowed
5.  Negative edge

Negative edges are important because Dijkstra should not be used where
negative edge weights violate its assumptions.

If negative weights are required, Bellman-Ford is more appropriate.

------------------------------------------------------------------------

# 130. Testing Knapsack

Use small manually verifiable cases.

Example:

``` text
capacity = 5

A: weight 2, value 6
B: weight 3, value 8
C: weight 4, value 9
```

Possible:

``` text
A+B = weight 5, value 14
C   = weight 4, value 9
```

So the optimal value is 14.

Such small cases help verify implementation before large datasets.

------------------------------------------------------------------------

# 131. Testing Graph Colouring

Test:

-   empty graph
-   one vertex
-   path
-   triangle
-   complete graph
-   disconnected graph

A triangle requires at least three colours under standard vertex
colouring because every pair of vertices is adjacent.

------------------------------------------------------------------------

# 132. Testing Branch-and-Bound

Compare:

``` text
branch-and-bound result
```

against:

``` text
brute-force result
```

for small inputs.

If both produce the same optimal answer on many small cases, confidence
in the implementation increases.

For large cases, brute force becomes too expensive, so the comparison
becomes less practical.

------------------------------------------------------------------------

# 133. Data Validation

A system working with surveillance data must validate:

-   missing values
-   duplicate records
-   invalid dates
-   impossible values
-   inconsistent locations
-   duplicate contacts
-   out-of-order events

The report explicitly highlights incomplete and late data as a
challenge.

Therefore, data validation should be treated as part of the system
rather than an afterthought.

------------------------------------------------------------------------

# 134. Handling Duplicate Patient Records

Suppose the same patient appears twice:

``` text
Patient ID = 412
Patient ID = 412
```

The system needs a policy.

Possible approach:

``` text
same ID
   |
check existing record
   |
update rather than duplicate
```

The exact policy must be specified by the implementation.

------------------------------------------------------------------------

# 135. Handling Duplicate Contacts

Suppose:

``` text
A -> B
```

is recorded multiple times.

The system could represent:

### Multiple event edges

``` text
A --event1-- B
A --event2-- B
```

or aggregate:

``` text
A ---- B
duration = total / weighted aggregation
```

The correct design depends on whether the system needs event-level or
relationship-level information.

------------------------------------------------------------------------

# 136. Privacy Considerations

Because patient records are involved, privacy is a major practical
consideration.

The report does not provide a detailed privacy architecture.

Therefore, any privacy mechanism discussed here should be treated as an
additional design consideration, not as an already-implemented feature.

A real system would need to consider:

-   access control
-   encryption
-   minimisation of personally identifying data
-   audit logs
-   secure storage
-   role-based permissions
-   data retention

------------------------------------------------------------------------

# 137. What Should Be Implemented First

The report's next-review plan starts with:

1.  AVL tree
2.  B+ tree
3.  Heap

This order makes sense because the index layer supports later modules.

Then:

4.  Contact graph
5.  BFS
6.  DFS
7.  Dijkstra
8.  Kruskal

Then:

9.  Dynamic programming
10. Knapsack
11. Greedy comparison

Then:

12. Graph colouring
13. Backtracking
14. Branch-and-bound
15. Routing

Finally:

16. Benchmarking

------------------------------------------------------------------------

# 138. Why Indexing Comes First

If the rest of the application constantly needs patient records, a
stable indexing layer is useful.

Conceptually:

``` text
Graph algorithm
      |
needs patient data
      |
index lookup
      |
AVL / B+ tree
```

Building the index first provides a reusable foundation.

------------------------------------------------------------------------

# 139. Why Graph Algorithms Come Second

Once patient and location records are accessible, relationships can be
constructed.

Then:

``` text
patient records
      +
contact records
      |
      v
contact graph
```

The graph becomes the basis for:

-   BFS
-   DFS
-   Dijkstra
-   MST
-   reachability

------------------------------------------------------------------------

# 140. Why DP Comes After the Graph Layer

The graph module generates information about:

-   clusters
-   connections
-   locations
-   risks

That information can become inputs to the resource-allocation model.

For example:

``` text
cluster information
       |
estimated need
       |
resource-allocation model
       |
knapsack
```

------------------------------------------------------------------------

# 141. Why Scheduling Comes Later

Scheduling has more complex combinatorial behaviour.

It is sensible to first have:

-   location information
-   priorities
-   graph relationships

before trying to optimise routes or zone assignments.

------------------------------------------------------------------------

# 142. Potential Viva Question: Why AVL Instead of Normal BST?

Answer:

> A normal BST can become skewed depending on insertion order, causing
> search, insertion and deletion to degrade to O(n). An AVL tree
> maintains a balance condition using rotations, keeping the tree height
> logarithmic and allowing these operations to remain O(log n).

------------------------------------------------------------------------

# 143. Potential Viva Question: Why B+ Tree?

Answer:

> B+ trees are designed for large, disk-backed indexes. Their high
> branching factor keeps the tree height low, reducing disk I/O, and
> linked leaf nodes make sequential range queries efficient.

------------------------------------------------------------------------

# 144. Potential Viva Question: Why BFS for Exposure Levels?

Answer:

> BFS explores vertices level by level using a queue. Therefore, in an
> unweighted contact graph, it naturally provides the minimum number of
> hops from a starting case to other reachable cases.

------------------------------------------------------------------------

# 145. Potential Viva Question: Why DFS for Clusters?

Answer:

> DFS can traverse an entire connected component before returning.
> Starting DFS from each unvisited vertex allows the system to identify
> connected components, which can represent computational clusters in
> the contact network.

------------------------------------------------------------------------

# 146. Potential Viva Question: Why Dijkstra?

Answer:

> The project represents contact relationships as weighted edges.
> Dijkstra can find the minimum-cost path from a source when edge
> weights are non-negative, so it can be used to compute paths under the
> project's defined contact-weight model.

------------------------------------------------------------------------

# 147. Potential Viva Question: Why Not Floyd-Warshall?

Answer:

> Floyd-Warshall computes all-pairs shortest paths but requires O(V³)
> time. That becomes expensive for a large contact network. It may still
> be useful on small district-level subgraphs, while larger graphs can
> use repeated single-source shortest-path algorithms where appropriate.

------------------------------------------------------------------------

# 148. Potential Viva Question: Why Dynamic Programming?

Answer:

> Resource allocation has a constrained optimisation structure and can
> exhibit optimal substructure. A 0/1 knapsack formulation allows the
> system to compute a maximum modeled benefit under a fixed capacity
> rather than relying only on a heuristic allocation.

------------------------------------------------------------------------

# 149. Potential Viva Question: Why Not Greedy?

Answer:

> A greedy approach makes locally attractive choices, but 0/1 knapsack
> does not guarantee that those choices produce a global optimum.
> Dynamic programming evaluates combinations through subproblem states
> and guarantees an optimum for the defined knapsack model.

------------------------------------------------------------------------

# 150. Potential Viva Question: Why Branch-and-Bound?

Answer:

> Problems such as TSP have very large combinatorial search spaces.
> Branch-and-bound explores possible solutions while using bounds to
> prune branches that cannot improve the current best solution, reducing
> unnecessary search compared with pure brute force.

------------------------------------------------------------------------

# 151. Potential Viva Question: What Is the Main Challenge?

A strong answer based directly on the report is:

> The major implementation challenges are maintaining correct AVL and
> threaded-tree pointers, dealing with the cubic complexity of
> Floyd-Warshall, constructing effective bounds for branch-and-bound,
> and handling incomplete or out-of-order surveillance data.

------------------------------------------------------------------------

# 152. Potential Viva Question: What Is the Main Contribution?

The project combines multiple DSA-II concepts into one domain-specific
computational system.

The contribution is not simply:

``` text
"I implemented AVL."
```

It is:

``` text
real-world problem
      |
computational decomposition
      |
appropriate DSA
      |
complexity analysis
      |
implementation
      |
benchmarking
```

That is the academic value of the project.

------------------------------------------------------------------------

# 153. Potential Weaknesses to Be Ready to Explain

The current report is a Month 1 progress report, so several parts are
still conceptual.

Be prepared to distinguish:

### Already defined

-   project scope
-   modules
-   DSA mapping
-   data model concept
-   complexity estimates
-   research foundation

### Still to implement

-   major data structures
-   graph algorithms
-   DP module
-   scheduling algorithms
-   benchmarking

### Still requiring design decisions

-   exact edge-weight formula
-   out-of-order data handling
-   strong branch-and-bound bound
-   final evaluation methodology
-   precise AI/forecasting component, if included

This distinction makes the project sound technically honest.

------------------------------------------------------------------------

# 154. A Clean Mental Model for the Entire Project

Memorise this:

``` text
PATIENT DATA
    |
    v
AVL / B+ TREE
    |
    | fast lookup
    v
CONTACT NETWORK
    |
    +---- BFS ------> exposure levels
    |
    +---- DFS ------> clusters
    |
    +---- DIJKSTRA -> weighted paths
    |
    +---- MST ------> minimum-cost connectivity
    |
    v
DECISION DATA
    |
    +---- KNAPSACK -> resource allocation
    |
    +---- LCS ------> timeline comparison
    |
    +---- COLOURING -> district zoning
    |
    +---- TSP/B&B -> collection routing
    |
    v
MONITORING / DECISION SUPPORT
```

------------------------------------------------------------------------

# 155. The Most Important Algorithms to Understand Deeply

If preparing for an exam or viva, prioritise these:

## Tier 1 --- Must understand

1.  BST
2.  AVL tree
3.  Heap
4.  BFS
5.  DFS
6.  Dijkstra
7.  0/1 Knapsack
8.  Backtracking
9.  Graph Colouring
10. Branch-and-Bound
11. TSP
12. B+ Tree

## Tier 2 --- Understand clearly

13. Prim
14. Kruskal
15. Bellman-Ford
16. Floyd-Warshall
17. Transitive Closure
18. LCS
19. Red-black trees
20. Fibonacci heaps
21. Binomial heaps
22. Threaded binary trees

## Tier 3 --- Know the concept and purpose

23. DAG
24. Matrix Chain Multiplication
25. N-Queens
26. Hamiltonian Cycle
27. Sum of Subsets

------------------------------------------------------------------------

# 156. One-Line Definitions for Revision

**Binary Tree:** A tree in which each node has at most two children.

**BST:** A binary tree maintaining an ordering between left and right
subtrees.

**AVL Tree:** A self-balancing BST whose balance factor remains between
-1 and +1.

**Heap:** A complete tree satisfying a heap-order property.

**B-Tree:** A balanced multiway search tree designed for efficient
external storage.

**B+ Tree:** A B-tree variant where records/pointers are stored at
leaves and leaves can be linked for efficient range access.

**Graph:** A collection of vertices connected by edges.

**BFS:** Graph traversal that explores level by level using a queue.

**DFS:** Graph traversal that explores deeply before backtracking using
recursion or a stack.

**Dijkstra:** Single-source shortest-path algorithm for graphs with
non-negative edge weights.

**Bellman-Ford:** Single-source shortest-path algorithm that can handle
negative edge weights.

**Floyd-Warshall:** Dynamic-programming algorithm for all-pairs shortest
paths.

**MST:** Minimum-weight tree connecting all vertices of a connected
weighted undirected graph.

**Prim:** Greedy MST algorithm that grows a tree from a starting vertex.

**Kruskal:** Greedy MST algorithm that adds the cheapest
non-cycle-forming edges.

**Transitive Closure:** Representation of reachability between every
pair of vertices.

**Dynamic Programming:** Solving overlapping subproblems once and
reusing their results.

**0/1 Knapsack:** Select or reject each item once to maximise value
under a capacity.

**LCS:** Finds the longest common subsequence of two sequences.

**Backtracking:** Search that abandons partial solutions when they
cannot lead to valid solutions.

**Branch-and-Bound:** Optimisation search that prunes branches that
cannot improve the best known solution.

**Graph Colouring:** Assign colours so adjacent vertices satisfy a
colouring constraint.

**TSP:** Find a minimum-cost tour visiting all required locations.

**DAG:** Directed graph containing no directed cycle.

**Red-Black Tree:** Self-balancing BST using node colours to constrain
height.

**Fibonacci Heap:** Advanced heap with strong amortized decrease-key
performance.

------------------------------------------------------------------------

# 157. Final Technical Summary

The entire project can be described in one paragraph:

> The AI-Based Disease Outbreak Monitoring System models surveillance
> records using balanced and external-memory search structures,
> represents contact and movement relationships as weighted graphs,
> analyses those graphs using traversal and shortest-path algorithms,
> allocates limited medical resources through dynamic programming, and
> handles combinatorial zoning and routing problems through graph
> colouring, backtracking and branch-and-bound. The project is evaluated
> not only by whether the algorithms work, but also by whether measured
> performance follows the expected complexity bounds and whether the
> chosen data structures remain practical as the dataset grows.

------------------------------------------------------------------------

# 158. Final Study Checklist

Before presenting the project, make sure you can explain all of the
following without reading notes.

## Trees

-   [ ] What is a tree?
-   [ ] What is a binary tree?
-   [ ] What is a BST?
-   [ ] BST search
-   [ ] BST insertion
-   [ ] BST deletion
-   [ ] Inorder traversal
-   [ ] Preorder traversal
-   [ ] Postorder traversal
-   [ ] AVL balance factor
-   [ ] LL rotation
-   [ ] RR rotation
-   [ ] LR rotation
-   [ ] RL rotation
-   [ ] Threaded tree
-   [ ] Binary heap

## Graphs

-   [ ] Vertex and edge
-   [ ] Directed vs undirected graph
-   [ ] Weighted graph
-   [ ] Adjacency matrix
-   [ ] Adjacency list
-   [ ] BFS
-   [ ] Queue in BFS
-   [ ] Visited array/set
-   [ ] DFS
-   [ ] Stack/recursion in DFS
-   [ ] Connected components
-   [ ] Dijkstra
-   [ ] Relaxation
-   [ ] Bellman-Ford
-   [ ] Floyd-Warshall
-   [ ] Prim
-   [ ] Kruskal
-   [ ] MST
-   [ ] Transitive closure
-   [ ] DAG

## Dynamic Programming

-   [ ] Optimal substructure
-   [ ] Overlapping subproblems
-   [ ] Memoization
-   [ ] Tabulation
-   [ ] 0/1 knapsack
-   [ ] Knapsack recurrence
-   [ ] LCS
-   [ ] LCS recurrence
-   [ ] Matrix Chain Multiplication
-   [ ] Resource allocation

## Backtracking / B&B

-   [ ] Backtracking
-   [ ] Search tree
-   [ ] Constraint checking
-   [ ] Graph colouring
-   [ ] N-Queens
-   [ ] Hamiltonian cycle
-   [ ] Sum of subsets
-   [ ] TSP
-   [ ] Branch
-   [ ] Bound
-   [ ] Pruning
-   [ ] Difference between backtracking and B&B

## Advanced Data Structures

-   [ ] Red-black tree
-   [ ] B-tree
-   [ ] B+ tree
-   [ ] Binomial heap
-   [ ] Fibonacci heap
-   [ ] Why B+ trees are useful for disk-backed storage
-   [ ] Why heaps are useful for priority queues

## Project

-   [ ] Problem statement
-   [ ] Four modules
-   [ ] Stakeholders
-   [ ] Literature review
-   [ ] Data model
-   [ ] Edge-weight meaning
-   [ ] Complexity estimates
-   [ ] Datasets
-   [ ] Challenges
-   [ ] Month 1 work
-   [ ] 25% progress
-   [ ] Next-review plan
-   [ ] Benchmarking strategy
-   [ ] Limitations of the computational interpretation

------------------------------------------------------------------------

# 159. The Core Story to Remember

Do not memorise the project as a random collection of algorithms.

Remember the story:

``` text
OUTBREAK
   |
   v
LOTS OF RECORDS
   |
   +--> Need fast lookup
   |        |
   |      AVL / B+ Tree
   |
   v
PEOPLE ARE CONNECTED
   |
   +--> Need exposure levels
   |        |
   |       BFS
   |
   +--> Need clusters
   |        |
   |       DFS
   |
   +--> Need weighted paths
   |        |
   |     Dijkstra
   |
   v
RESOURCES ARE LIMITED
   |
   +--> Need optimal allocation
   |        |
   |    Dynamic Programming
   |        |
   |    0/1 Knapsack
   |
   v
ACTIONS HAVE CONSTRAINTS
   |
   +--> Zone districts
   |       |
   |   Graph Colouring
   |
   +--> Plan routes
           |
       TSP + B&B
```

That is the entire DSA logic of the project.

------------------------------------------------------------------------

# 160. Bottom Line

The project is essentially a demonstration of how a single complex
real-world problem can be decomposed into smaller computational
problems, with each problem matched to an appropriate data structure or
algorithm.

The most important connections are:

``` text
Fast dynamic records       -> AVL / B+ Trees

Priority cases             -> Heaps

Contact relationships      -> Graphs

Hop-based exposure         -> BFS

Connected clusters         -> DFS

Weighted path analysis     -> Dijkstra

All-pairs path analysis    -> Floyd-Warshall

Network connectivity       -> Prim / Kruskal

Reachability               -> Transitive Closure

Limited resources          -> 0/1 Knapsack / DP

Timeline similarity        -> LCS

District zoning            -> Graph Colouring

Constraint search          -> Backtracking

Route optimisation         -> TSP / Branch-and-Bound
```

The project should ultimately demonstrate three things:

1.  **Correctness** --- the algorithms produce correct results for
    defined inputs.
2.  **Complexity awareness** --- the implementation behaves consistently
    with theoretical complexity expectations.
3.  **Practical mapping** --- every DSA technique has a clearly defined
    computational purpose in the outbreak-monitoring problem.

The current report establishes the design, research foundation and
feasibility analysis. The next stage is to turn those definitions into
working implementations, test them systematically, benchmark them, and
document where real-world data and theoretical assumptions diverge.
