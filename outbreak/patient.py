"""The record stored in the AVL tree (Unit 1).

A patient's id is also the patient's node index in the contact graph, so the same
number links all three units together.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Patient:
    id: int        # unique key, 0 <= id < number of graph nodes
    age: int       # years
    ward: int      # ward number, 0 <= ward < number of wards
    severity: int  # 1 (mild) .. 5 (critical)
