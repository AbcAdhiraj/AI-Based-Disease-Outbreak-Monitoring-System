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
