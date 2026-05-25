from dataclasses import dataclass, field
from src.parser.models import ParsedHub
from typing import List


# @dataclass
# class Hub:
#     name: str
#     coord_x: int
#     coord_y: int
#     color: str
#     max_capacity: int
#     connections: List["Connection"] = field(default_factory=list)


class Hub:
    def __init__(self, parsed_hub: ParsedHub):
        self.name = parsed_hub.name
        self.coord_x = parsed_hub.coord_x
        self.coord_y = parsed_hub.coord_y
        self.color = parsed_hub.meta.color
        self.max_capacity = parsed_hub.meta.max_drones
        self.connections: List["Connection"] = []


@dataclass
class Connection:
    hub_1: Hub
    hub_2: Hub
    color: str
    max_capacity: int
