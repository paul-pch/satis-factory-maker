from dataclasses import dataclass


@dataclass
class ProductionLine:
    item: str
    building: str
    num_machine: int
    time: int
    inputs: dict[str, float]  # {item_name: rate_per_min}
    outputs: dict[str, float]  # {item_name: rate_per_min}
    layer: int

    @classmethod
    def merge(cls, lines: list["ProductionLine"]) -> "ProductionLine":
        if len(lines) == 1:
            return lines[0]

        return cls(
            item=lines[0].item,
            building=lines[0].building,
            num_machine=sum(line.num_machine for line in lines),
            time=lines[0].time,
            inputs=lines[0].inputs,
            outputs=lines[0].outputs,
            layer=max(line.layer for line in lines),
        )
