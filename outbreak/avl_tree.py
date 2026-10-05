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
