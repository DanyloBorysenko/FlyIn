from typing import Dict, Tuple
from .models import Hub, Connection


class ReservationMap:
    def __init__(self):
        self.nodes: Dict[Tuple[Hub, int], int] = {}
        self.edges: Dict[Tuple[Connection, int], int] = {}

    def reserve_node(self, hub: Hub, turn: int) -> None:
        self.nodes[(hub, turn)] = self.nodes.get((hub, turn), 0) + 1

    def reserve_edge(self, connection: Connection, turn: int) -> None:
        self.edges[(connection, turn)] = self.edges.get(
            (connection, turn), 0) + 1

    def show_node_occupancy(self, hub: Hub, turn: int) -> int:
        return self.nodes.get((hub, turn), 0)

    def show_edge_occupancy(self, connection: Connection, turn: int) -> int:
        return self.edges.get((connection, turn), 0)


class Solver:
    def __init__(self):
        self.heuristics = self._calculate_heuristics()

    def _calculate_heuristics(self) -> Dict[str, float]:

        return {}
