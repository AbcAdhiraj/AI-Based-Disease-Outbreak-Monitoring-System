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
