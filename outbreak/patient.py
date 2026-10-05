"""The record stored in the AVL tree (Unit 1).

A patient's id is also the patient's node number in the contact graph,
so the same number links all three units together.
"""


class Patient:
    def __init__(self, id, age, ward, severity):
        self.id = id              # unique key, 0 <= id < number of graph nodes
        self.age = age            # age in years
        self.ward = ward          # ward number, 0 <= ward < number of wards
        self.severity = severity  # 1 (mild) up to 5 (critical)

    def __repr__(self):
        # Only used when printing a Patient while debugging.
        return "Patient(id=%d, age=%d, ward=%d, severity=%d)" % (
            self.id, self.age, self.ward, self.severity)
