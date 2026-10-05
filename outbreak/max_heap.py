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
