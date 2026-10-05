"""Synthetic (made-up) data for the project, plus an optional real-data loader.

Every function takes a `seed`. The same seed always gives the same data, so
results can be repeated exactly.
"""
import csv
import os
import random

from .allocation import Option
from .graph import Graph
from .patient import Patient


def generate_contact_graph(n, avg_degree, seed):
    """Random contact graph with n nodes and the given average degree.

    Average degree = 2 * (number of edges) / n, so we need n * avg_degree / 2 edges.
    We repeatedly pick two random different patients and connect them, skipping
    pairs that are already connected.
    Contact duration is random in 0.2..6 hours and proximity in 0.1..1 (assumptions).
    """
    graph = Graph(n)
    if n < 2:
        return graph
    rng = random.Random(seed)
    wanted_edges = int(n * avg_degree / 2)
    most_possible = n * (n - 1) // 2          # a graph cannot have more edges than this
    if wanted_edges > most_possible:
        wanted_edges = most_possible

    used_pairs = set()                        # pairs that already have an edge
    while len(used_pairs) < wanted_edges:
        u = rng.randrange(n)
        v = rng.randrange(n)
        if u == v:
            continue                          # a patient cannot contact themselves
        if u < v:
            pair = (u, v)
        else:
            pair = (v, u)                     # (3, 5) and (5, 3) are the same edge
        if pair in used_pairs:
            continue
        used_pairs.add(pair)
        duration = rng.uniform(0.2, 6.0)
        proximity = rng.uniform(0.1, 1.0)
        graph.add_edge(u, v, duration, proximity)
    return graph


def generate_patients(n, num_wards, seed):
    """n random patients with ids 0..n-1 (the id is also the graph node number)."""
    rng = random.Random(seed)
    patients = []
    for i in range(n):
        age = rng.randint(1, 90)
        ward = rng.randrange(num_wards)
        severity = rng.randint(1, 5)
        patients.append(Patient(i, age, ward, severity))
    return patients


def synthetic_case_series(num_wards, days, seed):
    """Made-up daily case counts, one list per ward.

    Each ward starts at 20..100 cases and changes by its own daily rate
    (between -8% and +12%) plus a little random noise (+/- 5%).
    """
    rng = random.Random(seed)
    all_series = []
    for w in range(num_wards):
        value = rng.uniform(20, 100)
        rate = rng.uniform(-0.08, 0.12)
        series = []
        for d in range(days):
            series.append(value)
            noise = rng.uniform(-0.05, 0.05)
            value = value * (1.0 + rate + noise)
            if value < 0:
                value = 0.0                   # case counts cannot be negative
        all_series.append(series)
    return all_series


def load_jhu_csv(path):
    """Read a Johns Hopkins CSSE file (time_series_covid19_confirmed_global.csv).

    Each row is: Province/State, Country/Region, Lat, Long, then one column per
    date holding the CUMULATIVE confirmed cases. We return one list of numbers per
    row, or [] if the file does not exist or cannot be read.
    (The csv module is used because names like "Korea, South" contain commas.)
    """
    if not os.path.isfile(path):
        return []
    rows = []
    try:
        with open(path, newline="") as f:
            reader = csv.reader(f)
            next(reader, None)                # skip the header line
            for fields in reader:
                if len(fields) <= 4:
                    continue                  # no date columns: skip
                numbers = []
                for text in fields[4:]:       # the first 4 columns are labels
                    if text == "":
                        numbers.append(0.0)
                    else:
                        numbers.append(float(text))
                rows.append(numbers)
    except (OSError, ValueError):
        return []                             # unreadable or malformed file
    return rows


def case_series_for_wards(path, num_wards, days, seed):
    """Daily case series for each ward. Returns (series, used_real_data).

    If the CSV exists and has enough rows and days we use it, converting the
    cumulative totals into daily NEW cases (today minus yesterday, never below 0).
    Otherwise we fall back to synthetic data.
    """
    rows = load_jhu_csv(path)
    enough = len(rows) >= num_wards
    if enough:
        for w in range(num_wards):
            if len(rows[w]) <= days:
                enough = False                # this row has too few days
    if not enough:
        return synthetic_case_series(num_wards, days, seed), False

    series = []
    for w in range(num_wards):
        cumulative = rows[w]
        daily = []
        for t in range(len(cumulative) - days, len(cumulative)):   # the last `days` days
            new_cases = cumulative[t] - cumulative[t - 1]
            if new_cases < 0:
                new_cases = 0.0               # corrections in the data can go negative
            daily.append(new_cases)
        series.append(daily)
    return series, True


def random_allocation_instance(num_wards, options_per_ward, seed):
    """A random knapsack problem for tests and benchmarks.

    Every ward gets Option(0, 0) first, then more options where both cost and
    value increase step by step (so bigger packages avert more cases).
    """
    rng = random.Random(seed)
    wards = []
    for w in range(num_wards):
        options = [Option(0, 0.0)]
        for k in range(1, options_per_ward):
            last = options[-1]
            new_cost = last.cost + rng.randint(1, 4)
            new_value = last.value + rng.uniform(0.5, 6.0)
            options.append(Option(new_cost, new_value))
        wards.append(options)
    return wards
