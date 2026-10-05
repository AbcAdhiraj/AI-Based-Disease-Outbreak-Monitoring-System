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
