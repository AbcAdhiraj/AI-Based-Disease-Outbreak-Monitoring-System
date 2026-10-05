"""Glue between Unit 2 (graph) and Units 1 and 3."""
import math
from typing import List

from .allocation import Option, WardOptions
from .graph import Graph
from .max_heap import MaxHeap
from .patient import Patient

# MODEL ASSUMPTION: four supply packages per ward with diminishing returns.
PACKAGE_COSTS = (0, 2, 4, 6)
PACKAGE_EFFECT = (0.0, 0.40, 0.65, 0.80)  # fraction of expected cases averted


def node_risk(g: Graph, infected: List[int]) -> List[float]:
    """risk(v) = 1 - prod over infected u of (1 - exp(-dist(u, v))).

    MODEL ASSUMPTION (not validated epidemiology): Dijkstra's dist(u, v) equals
    -ln(probability of the best path u->v), so exp(-dist) is that path's
    probability. "Infection reaches v from u" is that event, and different
    infected sources are treated as independent, giving the usual "at least one
    source succeeds" formula. An infected node has dist 0 to itself, a factor
    (1 - 1) = 0, so its risk is exactly 1.
    Complexity: one Dijkstra per source, O(k (V + E) log V) for k sources.
    """
    survive = [1.0] * len(g)  # probability of escaping every source
    for source in infected:
        dist = g.likely_path(source).dist
        for v, d in enumerate(dist):
            reach = 0.0 if math.isinf(d) else math.exp(-d)
            survive[v] *= 1.0 - reach
    return [1.0 - s for s in survive]


def ward_risk(patients: List[Patient], risk: List[float], num_wards: int) -> List[float]:
    """Mean node risk per ward. O(P). The mean is size-independent, so wards compare fairly."""
    total, count = [0.0] * num_wards, [0] * num_wards
    for p in patients:
        total[p.ward] += risk[p.id]
        count[p.ward] += 1
    return [t / c if c else 0.0 for t, c in zip(total, count)]


def ward_expected_cases(patients: List[Patient], risk: List[float],
                        is_infected: List[bool], num_wards: int) -> List[float]:
    """Expected NEW cases per ward: the sum of risks of not-yet-infected patients
    (linearity of expectation, no independence needed). Infected patients are
    excluded because their cases cannot be "averted"."""
    expected = [0.0] * num_wards
    for p in patients:
        if not is_infected[p.id]:
            expected[p.ward] += risk[p.id]
    return expected


def build_risk_heap(risk: List[float], is_infected: List[bool]) -> MaxHeap:
    """Heap of (patient id, risk) for patients not already infected. O(P log P)."""
    heap = MaxHeap()
    for v, r in enumerate(risk):
        if not is_infected[v]:
            heap.push(v, r)
    return heap


def build_ward_options(expected_cases: List[float]) -> WardOptions:
    """Packages cost 0/2/4/6 units averting 0/40/65/80 % of a ward's expected cases.

    Diminishing returns is what turns the allocation into a real trade-off.
    """
    return [[Option(c, cases * e) for c, e in zip(PACKAGE_COSTS, PACKAGE_EFFECT)]
            for cases in expected_cases]
