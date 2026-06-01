from typing import Dict, Tuple
from .models import Hub, Connection, SimulationMap, StepPath
from src.domain import ZoneType
import heapq


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
    def __init__(self, map: SimulationMap) -> None:
        self.map = map
        self.zone_priorities = {
            ZoneType.NORMAL: 1.0,
            ZoneType.RESTRICTED: 2.0,
            ZoneType.PRIORITY: 0.9
        }
        self.heuristics = self._calculate_heuristics()

    def _calculate_heuristics(self) -> Dict[Hub, float]:
        end = self.map.end_hub
        heuristics = {end: 0.0}
        heap = [(0.0, end.name, end)]
        while heap:
            cost, _, hub = heapq.heappop(heap)
            for neighbour in hub.get_neighbours():
                if neighbour.zone_type == ZoneType.BLOCKED:
                    continue
                new_cost = cost + self.zone_priorities[neighbour.zone_type]
                if (neighbour not in heuristics
                   or new_cost < heuristics[neighbour]):
                    heuristics[neighbour] = new_cost
                    heapq.heappush(heap, (new_cost, neighbour.name, neighbour))
        return heuristics

    def print_heuristic(self) -> None:
        for hub, cost in self.heuristics.items():
            print(f"Hub: {hub.name}, cost: {cost}")

    def solve(self) -> None:
        for dron in self.map.drones:
            for hub in self.map.hubs.values():
                dron.steps.append(StepPath(hub))
        self.map.drones[1].steps[2] = StepPath(self.map.hubs["path_b"])
