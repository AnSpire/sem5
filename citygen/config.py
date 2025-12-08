from dataclasses import dataclass

@dataclass
class CityConfig:
    GRID: int = 6
    CELL: float = 300
    OFFSET: float = 25
    MIN_D: float = 200
    MAX_D: float = 500
    CURVED_PROB: float = 0.5

    BRANCH_PROB: float = 0.65
    BRANCH_MIN: float = 0.2
    BRANCH_MAX: float = 0.45

    HOUSE_INSIDE_MIN: tuple = (5,9)

    SHOW_LOCAL: bool = False
