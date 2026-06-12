from src.parser import ParsedHub
from typing import List, Dict, Any
from dataclasses import dataclass, field


class Hub:
    def __init__(self, parsed_hub: ParsedHub) -> None:
        self.name = parsed_hub.name
        self.kind = parsed_hub.kind
        self.coord_x = float(parsed_hub.coord_x)
        self.coord_y = float(parsed_hub.coord_y)
        self.zone_type = parsed_hub.meta.zone
        self.color = parsed_hub.meta.color
        self.max_capacity = parsed_hub.meta.max_drones
        self.nb_drones = 0
        self.connections: List["Connection"] = []
        self.neighbours: Dict["Hub", Connection] = {}

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

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, value: Any) -> bool:
        return isinstance(value, Connection) and self.name == value.name

    def __repr__(self) -> str:
        return (f"Connection: {self.name}"
                f"\n coord_x: {self.coord_x}, coord_y: {self.coord_y}")


class Node:
    def __init__(self,
                 location: Hub,
                 turn: int,
                 h_cost: float) -> None:
        self.location = location
        self.turn = turn
        self.h_cost = h_cost

    def __lt__(self, other: "Node") -> bool:
        return self.h_cost < other.h_cost

    def __eq__(self, value: Any) -> bool:
        return isinstance(value, Node) and self.location == value.location

    def __repr__(self) -> str:
        return (f"Location: {self.location.name} "
                f"Turn: {self.turn} "
                f"h_cost: {self.h_cost} "
                f"Movement: {self.movement_str} ")


class Drone:
    def __init__(self, id: int) -> None:
        self.id = f"D{id}"
        self.steps: List[Hub | Connection] = []
        self.steps_count: int = 0

    def __eq__(self, value: Any) -> bool:
        return isinstance(value, Drone) and value.id == self.id

    def __hash__(self) -> int:
        return hash(self.id)


@dataclass
class Analytics:
    max_turn: int = 0
    min_turn: int = 0
    drones_count: int = 0
    turns_output: List[str] = field(default_factory=list)


@dataclass
class Simulation:
    name: str
    start_hub: Hub
    end_hub: Hub
    hubs: Dict[str, Hub]
    connections: Dict[str, Connection]
    drones: List[Drone]
    analytics: Analytics

    def __repr__(self) -> str:
        return (f"\nStart hub: {self.start_hub}\n"
                f"End hub: {self.end_hub}\n"
                f"Hubs: {self.hubs}\n"
                f"Connections: {self.connections}\n"
                f"Drones: {self.drones}")
