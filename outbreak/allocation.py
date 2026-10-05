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
