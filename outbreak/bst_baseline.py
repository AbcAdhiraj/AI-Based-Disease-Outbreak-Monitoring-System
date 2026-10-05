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
