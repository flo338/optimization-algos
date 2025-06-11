from enum import StrEnum, auto


class Algorithm(StrEnum):
    HILL_CLIMBING = "Hill Climbing"
    SIMULATED_ANNEALING = "Simulated Annealing"
    BACKTRACKING = "Backtracking"

class Neighborhoods(StrEnum):
    GEOMETRIC = auto()
    RULE_BASED = auto()
    RELAXED_GEOMETRIC = auto()
