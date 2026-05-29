from src.parser import ParsedHub
from typing import List, Dict, Any
from dataclasses import dataclass


class Hub:
    def __init__(self, parsed_hub: ParsedHub) -> None:
        self.name = parsed_hub.name
        self.kind = parsed_hub.kind
        self.coord_x = parsed_hub.coord_x
        self.coord_y = parsed_hub.coord_y
        self.zone_type = parsed_hub.meta.zone
        self.color = parsed_hub.meta.color
        self.max_capacity = parsed_hub.meta.max_drones
        self.nb_drones = 0
        self.connections: List["Connection"] = []

    def __repr__(self) -> str:
        return ("Hub:\n"
                f"Name: {self.name}\n"
                f"Color: {self.color}")

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, value: Any) -> bool:
        return isinstance(value, Hub) and self.name == value.name


class Connection:
    def __init__(self, hub_1: Hub, hub_2: Hub, capacity: int) -> None:
        self.name = "-".join(sorted([hub_1.name, hub_2.name]))
        self.hub_1 = hub_1
        self.hub_2 = hub_2
        self.color = "white"
        self.max_capacity = capacity
        self.nb_drones = 0

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, value: Any) -> bool:
        return isinstance(value, Connection) and self.name == value.name


class Drone:
    def __init__(self, id: int) -> None:
        self.id = id
        self.current_zone: Hub | None = None
        self.current_connection: Connection | None = None


@dataclass
class SimulationMap:
    start_hub: Hub
    end_hub: Hub
    hubs: Dict[str, Hub]
    connections: List[Connection]
    drones: List[Drone]

    def __repr__(self) -> str:
        return (f"\nStart hub: {self.start_hub}\n"
                f"End hub: {self.end_hub}\n"
                f"Hubs: {self.hubs}\n"
                f"Connections: {self.connections}\n"
                f"Drones: {self.drones}")
