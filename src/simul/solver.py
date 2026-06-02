from typing import Dict, Tuple
from .models import Hub, Connection, Simulation, StepPath
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
    def __init__(self, simul: Simulation) -> None:
        self.simul = simul
        self.zone_priorities = {
            ZoneType.NORMAL: 1.0,
            ZoneType.RESTRICTED: 2.0,
            ZoneType.PRIORITY: 0.9
        }
        self.heuristics = self._calculate_heuristics()
        self.reserv_map = ReservationMap()

    def _calculate_heuristics(self) -> Dict[Hub, float]:
        end = self.simul.end_hub
        heuristics = {end: 0.0}
        heap = [(0.0, end.name, end)]
        while heap:
            cost, _, hub = heapq.heappop(heap)
            for neighbour in hub.get_neighbours():
                if neighbour.zone_type == ZoneType.BLOCKED:
                    continue
                new_cost = cost + self.zone_priorities[hub.zone_type]
                if (neighbour not in heuristics
                   or new_cost < heuristics[neighbour]):
                    heuristics[neighbour] = new_cost
                    heapq.heappush(heap, (new_cost, neighbour.name, neighbour))
        return dict(sorted(heuristics.items(), key=lambda item: item[1]))

    def print_heuristic(self) -> None:
        for hub, cost in self.heuristics.items():
            print(f"Hub: {hub.name}, cost: {cost}")

    def solve(self) -> None:
        for dron in self.simul.drones:
            turn = 0
            while (dron.steps[-1].location != self.simul.end_hub):
                cur_loc = dron.steps[-1].location
                next_loc = cur_loc
                if isinstance(cur_loc, Connection):
                    next_loc = cur_loc.get_oposssite(
                        dron.steps[-2].location)
                else:
                    neighbours = cur_loc.get_neighbours()
                    for hub in self.heuristics.keys():
                        if hub in neighbours:
                            if hub.zone_type == ZoneType.NORMAL:
                                free = self.reserv_map.show_node_occupancy(
                                    hub, turn + 1) < hub.max_capacity
                                if free:
                                    next_loc = hub
                                    self.reserv_map.reserve_node(next_loc, turn + 1)
                                    break
                            else:
                                free = self.reserv_map.show_node_occupancy(
                                    hub, turn + 2) < hub.max_capacity
                                if free:
                                    conn = self.simul.connections["-".join(
                                        sorted([cur_loc.name, hub.name]))]
                                    free = self.reserv_map.show_edge_occupancy(
                                        conn,
                                        turn + 1
                                    ) < conn.max_capacity
                                    if free:
                                        next_loc = conn
                                        self.reserv_map.reserve_edge(next_loc, turn + 1)
                                        self.reserv_map.reserve_node(hub, turn + 2)
                                        break
                dron.steps.append(StepPath(next_loc))
                turn += 1
