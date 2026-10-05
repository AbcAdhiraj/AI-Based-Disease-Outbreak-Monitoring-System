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
