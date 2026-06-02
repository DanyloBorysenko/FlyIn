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

    def get_neighbours(self) -> List[Hub]:
        neighbours = []
        for conn in self.connections:
            hub1 = conn.hub_1
            hub2 = conn.hub_2
            if self == hub1:
                neighbours.append(hub2)
            elif self == hub2:
                neighbours.append(hub1)
        return neighbours

    def __repr__(self) -> str:
        return f"Hub: {self.name}"

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, value: Any) -> bool:
        return isinstance(value, Hub) and self.name == value.name


class Connection:
    def __init__(self, hub_1: Hub, hub_2: Hub, capacity: int) -> None:
        self.name = "-".join(sorted([hub_1.name, hub_2.name]))
        self.hub_1 = hub_1
        self.hub_2 = hub_2
        self.coord_x = (hub_1.coord_x + hub_2.coord_x) / 2
        self.coord_y = (hub_1.coord_y + hub_2.coord_y) / 2
        self.color = "black"
        self.max_capacity = capacity
        self.nb_drones = 0

    def get_oposssite(self, hub: Hub) -> Hub:
        if hub == self.hub_1:
            return self.hub_2
        elif hub == self.hub_2:
            return self.hub_1

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, value: Any) -> bool:
        return isinstance(value, Connection) and self.name == value.name

    def __repr__(self) -> str:
        return (f"Connection: {self.name}"
                f"\n coord_x: {self.coord_x}, coord_y: {self.coord_y}")


@dataclass
class StepPath:
    location: Hub | Connection


class Drone:
    def __init__(self, id: int) -> None:
        self.id = f"D{id}"
        self.steps: List[StepPath] = []

    def __eq__(self, value: Any) -> bool:
        return isinstance(value, Drone) and value.id == self.id

    def __hash__(self) -> int:
        return hash(self.id)


@dataclass
class Simulation:
    start_hub: Hub
    end_hub: Hub
    hubs: Dict[str, Hub]
    connections: Dict[str, Connection]
    drones: List[Drone]

    def __repr__(self) -> str:
        return (f"\nStart hub: {self.start_hub}\n"
                f"End hub: {self.end_hub}\n"
                f"Hubs: {self.hubs}\n"
                f"Connections: {self.connections}\n"
                f"Drones: {self.drones}")
