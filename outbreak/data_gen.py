"""Synthetic inputs (seeded, reproducible) plus an optional real-data loader."""
import csv
import os
import random
from typing import List, Optional, Tuple

from .allocation import Option, WardOptions
from .graph import Graph
from .patient import Patient


def generate_contact_graph(n: int, avg_degree: float, seed: int) -> Graph:
    """Random graph with about n * avg_degree / 2 distinct undirected edges. O(m).

    Each edge joins two random distinct nodes; a set of used pairs prevents
    duplicates. Average degree = 2m / n, so we draw m = n * avg_degree / 2 edges
    (capped at n(n-1)/2). Duration 0.2..6 h and proximity 0.1..1, uniform: model assumptions.
    """
    g = Graph(n)
    if n < 2:
        return g
    rng = random.Random(seed)
    target = min(n * (n - 1) // 2, int(n * avg_degree / 2))
    used = set()
    while len(used) < target:
        u, v = rng.randrange(n), rng.randrange(n)
        if u == v:
            continue
        key = (u, v) if u < v else (v, u)
        if key in used:
            continue
        used.add(key)
        g.add_edge(u, v, rng.uniform(0.2, 6.0), rng.uniform(0.1, 1.0))
    return g


def generate_patients(n: int, num_wards: int, seed: int) -> List[Patient]:
    """n patients with id = 0..n-1 (id == graph node index)."""
    rng = random.Random(seed)
    return [Patient(i, rng.randint(1, 90), rng.randrange(num_wards), rng.randint(1, 5))
            for i in range(n)]


def synthetic_case_series(num_wards: int, days: int, seed: int) -> List[List[float]]:
    """Fake daily case counts: each ward gets a growth rate in [-8%, +12%] per day,
    +-5% noise, starting from 20..100 cases."""
    rng = random.Random(seed)
    all_series = []
    for _ in range(num_wards):
        value, rate = rng.uniform(20, 100), rng.uniform(-0.08, 0.12)
        series = []
        for _ in range(days):
            series.append(value)
            value = max(0.0, value * (1.0 + rate + rng.uniform(-0.05, 0.05)))
        all_series.append(series)
    return all_series


def load_jhu_csv(path: str) -> List[List[float]]:
    """Read a Johns Hopkins CSSE confirmed-cases CSV (time_series_covid19_confirmed_global.csv).

    Format: Province/State,Country/Region,Lat,Long,<one column per date>...
    The first four columns are labels; the rest are cumulative confirmed counts.
    Returns one cumulative series per row, or [] if the file is missing/unreadable.
    The csv module handles quoted commas such as "Korea, South".
    """
    if not os.path.isfile(path):
        return []
    rows = []
    try:
        with open(path, newline="") as f:
            reader = csv.reader(f)
            next(reader, None)  # header
            for fields in reader:
                if len(fields) > 4:
                    rows.append([float(x) if x else 0.0 for x in fields[4:]])
    except (OSError, ValueError):
        return []
    return rows


def case_series_for_wards(path: str, num_wards: int, days: int,
                          seed: int) -> Tuple[List[List[float]], bool]:
    """Ward trend data: (series, used_real_data).

    Uses the first `num_wards` CSV rows (last `days` days) if the file loads and
    is big enough, converting cumulative totals to daily new cases (negative
    corrections clamp to 0). Otherwise falls back to synthetic series.
    """
    rows = load_jhu_csv(path)
    if len(rows) < num_wards or any(len(r) <= days for r in rows[:num_wards]):
        return synthetic_case_series(num_wards, days, seed), False
    out = []
    for cum in rows[:num_wards]:
        n = len(cum)
        out.append([max(0.0, cum[t] - cum[t - 1]) for t in range(n - days, n)])
    return out, True


def random_allocation_instance(num_wards: int, options_per_ward: int, seed: int) -> WardOptions:
    """Random knapsack instance: every ward has (0,0) plus options with increasing
    cost (+1..4 each step) and value (+0.5..6 each step), so bigger packages avert more."""
    rng = random.Random(seed)
    wards = []
    for _ in range(num_wards):
        options = [Option(0, 0.0)]
        for _ in range(1, options_per_ward):
            last = options[-1]
            options.append(Option(last.cost + rng.randint(1, 4), last.value + rng.uniform(0.5, 6.0)))
        wards.append(options)
    return wards
