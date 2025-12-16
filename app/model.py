from dataclasses import dataclass


@dataclass
class ProductionLine:
    item: str
    building: str
    num_machine: int
    inputs: dict[str, float]  # {item_name: rate_per_min}
    outputs: dict[str, float]  # {item_name: rate_per_min}
    layer: int
