from typing import Dict, Tuple, List, Any
from .models import Hub, Connection, Simulation, Node, Analytics
from src.domain import ZoneType
import heapq


class ReservationMap:
    def __init__(self):
        self.nodes: Dict[Tuple[Hub, int], int] = {}
        self.edges: Dict[Tuple[Connection, int], int] = {}

    def reserve_hub(self, hub: Hub, turn: int) -> None:
        self.nodes[(hub, turn)] = self.nodes.get((hub, turn), 0) + 1

    def reserve_loc(self, connection: Connection, turn: int) -> None:
        self.edges[(connection, turn)] = self.edges.get(
            (connection, turn), 0) + 1

    def show_hub_occupancy(self, hub: Hub, turn: int) -> int:
        return self.nodes.get((hub, turn), 0)

    def show_conn_occupancy(self, connection: Connection, turn: int) -> int:
        return self.edges.get((connection, turn), 0)


class Solver:
    def __init__(self) -> None:
        self.zone_priorities = {
            ZoneType.NORMAL: 1.0,
            ZoneType.RESTRICTED: 2.0,
            ZoneType.PRIORITY: 0.9
        }

    def _calculate_heuristics(self, simul: Simulation) -> Dict[Hub, float]:
        end = simul.end_hub
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

    def _get_turn_movement(self, turn: int, simul: Simulation) -> str:
        line = ""
        for drone in simul.drones:
            if turn > 0 and turn < len(drone.steps):
                if drone.steps[turn - 1] == drone.steps[turn]:
                    continue
                line = f"{line} {drone.steps[turn].movement_str}"
        return line

    def show_all_turns(self, simul: Simulation) -> None:
        max_turn = simul.analitics.max_turn
        print(f"Max turns: {max_turn - 1}")
        for turn in range(1, max_turn + 1):
            print(self._get_turn_movement(turn, simul))

    def solve(self, simulations: List[Tuple[str, Simulation]]) -> None:
        for name, simul in simulations:
            reserv_map = ReservationMap()
            for drone in simul.drones:
                path: List[Node] = self._find_path(drone.id, simul, reserv_map)
                drone.steps.extend(path)
                for turn, node in enumerate(path[1:-1], 1):
                    if isinstance(node.location, Hub):
                        reserv_map.reserve_hub(node.location, turn)
                    else:
                        reserv_map.reserve_loc(node.location, turn)
            simul.analitics = self.get_simul_analitics(simul)

    def get_simul_analitics(self, simul: Simulation) -> Analytics:
        paths: Dict[str, List[Node]] = {}
        for drone in simul.drones:
            paths[drone.id] = drone.steps
        max_turn = max(
            [len(steps) for steps in paths.values()])
        min_turn = min(
            [len(steps) for steps in paths.values()])
        return Analytics(max_turn, min_turn)

    def _find_path(self, drone_id: str, simul: Simulation, reserv_map: ReservationMap) -> List[Node]:
        possible_steps: List[Node] = []
        path: List[Node] = []
        heuristics = self._calculate_heuristics(simul)
        first_node = Node(
            location=simul.start_hub,
            turn=0,
            drone_id=drone_id,
            h_cost=heuristics[simul.start_hub],
            t_cost=0)
        heapq.heappush(possible_steps, first_node)
        while possible_steps:
            current = heapq.heappop(possible_steps)
            curr_location = current.location
            if curr_location.zone_type == ZoneType.RESTRICTED:
                for conn in curr_location.connections:
                    if curr_location.name in conn.name and path[-1].location.name in conn.name:
                        mid_conn_step = Node(conn, current.turn - 1, drone_id, current.h_cost, current.t_cost)
                        path.append(mid_conn_step)
            path.append(current)
            if curr_location == simul.end_hub:
                return path
            possible_steps.clear()
            for conn in curr_location.connections:
                neighbour = conn.get_oposssite(curr_location)
                if neighbour.zone_type == ZoneType.BLOCKED:
                    continue
                step_cost = 2 if (
                    neighbour.zone_type == ZoneType.RESTRICTED) else 1
                next_turn = current.turn + step_cost
                if neighbour != simul.end_hub:
                    hub_ocup = reserv_map.show_hub_occupancy(
                        neighbour, next_turn)
                    if hub_ocup >= neighbour.max_capacity:
                        continue
                conn_ocup = reserv_map.show_conn_occupancy(
                    conn, current.turn + 1)
                if conn_ocup >= conn.max_capacity:
                    continue
                possible_step = Node(
                    neighbour,
                    next_turn,
                    drone_id,
                    heuristics[neighbour],
                    current.t_cost + step_cost)
                heapq.heappush(possible_steps, possible_step)
            next_ocup = reserv_map.show_hub_occupancy(
                curr_location, current.turn + 1
            )
            if (curr_location == simul.start_hub
               or next_ocup <= curr_location.max_capacity):
                wait_step = Node(
                    curr_location,
                    current.turn + 1,
                    drone_id,
                    heuristics[curr_location],
                    current.turn + 1
                )
                heapq.heappush(possible_steps, wait_step)
        return []
