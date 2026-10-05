"""Glue between the units: graph results -> risk scores -> heap and allocation options."""
import math

from .allocation import Option
from .max_heap import MaxHeap

# MODEL ASSUMPTION: each ward can get one of four supply packages.
# More spending averts more cases, but with diminishing returns.
PACKAGE_COSTS = [0, 2, 4, 6]                  # budget units
PACKAGE_EFFECT = [0.0, 0.40, 0.65, 0.80]      # fraction of expected cases averted


def node_risk(graph, infected):
    """Risk of every patient, given the list of infected patients.

    risk(v) = 1 - product over infected sources u of (1 - exp(-dist(u, v)))

    MODEL ASSUMPTION (not validated epidemiology):
      * dist(u, v) from Dijkstra is -ln(probability of the best path u -> v),
        so exp(-dist) is the chance that infection travels from u to v.
      * (1 - that chance) is the chance source u does NOT infect v.
      * Treating sources as independent, the chance that NO source infects v is
        the product of those numbers, and the risk is 1 minus it.
    An infected patient has distance 0 to itself, so its factor is (1 - 1) = 0
    and its risk is exactly 1.
    Time: one Dijkstra per infected source.
    """
    # not_infected[v] = chance that v escapes every source seen so far (starts at 1).
    not_infected = [1.0] * len(graph)
    for source in infected:
        dist = graph.likely_path(source).dist
        for v in range(len(graph)):
            if math.isinf(dist[v]):
                reach = 0.0                   # unreachable: this source cannot infect v
            else:
                reach = math.exp(-dist[v])    # chance that infection reaches v
            not_infected[v] = not_infected[v] * (1.0 - reach)

    risk = []
    for v in range(len(graph)):
        risk.append(1.0 - not_infected[v])
    return risk


def ward_risk(patients, risk, num_wards):
    """Average risk of the patients in each ward (the mean makes wards of
    different sizes comparable)."""
    total = [0.0] * num_wards
    count = [0] * num_wards
    for patient in patients:
        total[patient.ward] += risk[patient.id]
        count[patient.ward] += 1
    result = []
    for w in range(num_wards):
        if count[w] > 0:
            result.append(total[w] / count[w])
        else:
            result.append(0.0)
    return result


def ward_expected_cases(patients, risk, is_infected, num_wards):
    """Expected number of NEW cases in each ward.

    Adding up each patient's risk gives the expected count. Patients who are
    already infected are skipped because their cases cannot be averted.
    """
    expected = [0.0] * num_wards
    for patient in patients:
        if not is_infected[patient.id]:
            expected[patient.ward] += risk[patient.id]
    return expected


def build_risk_heap(risk, is_infected):
    """Put (patient id, risk) into a max-heap, skipping already-infected patients."""
    heap = MaxHeap()
    for v in range(len(risk)):
        if not is_infected[v]:
            heap.push(v, risk[v])
    return heap


def build_ward_options(expected_cases):
    """For each ward, create the four packages. A package averts
    (expected cases of the ward) x (its effect fraction)."""
    wards = []
    for cases in expected_cases:
        options = []
        for k in range(len(PACKAGE_COSTS)):
            options.append(Option(PACKAGE_COSTS[k], cases * PACKAGE_EFFECT[k]))
        wards.append(options)
    return wards
