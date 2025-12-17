from dataclasses import dataclass
from typing import TypedDict


class Recipe(TypedDict):
    name: str
    key_name: str
    category: str
    time: int
    ingredients: list[tuple[str, float]]
    products: list[tuple[str, float]]


@dataclass
class ProductionLine:
    item: str
    building: str
    num_machine: int
    recipe: Recipe
    layer: int

    @classmethod
    def merge(cls, lines: list["ProductionLine"]) -> "ProductionLine":
        if len(lines) == 1:
            return lines[0]

        return cls(
            item=lines[0].item,
            building=lines[0].building,
            num_machine=sum(line.num_machine for line in lines),
            recipe=lines[0].recipe,
            layer=max(line.layer for line in lines),
        )
