from typing import Dict, Tuple, List
from .models import Hub, Connection, Simulation, Node, Analytics
from src.domain import ZoneType
from .errors import SimulationError
import heapq


class ReservationMap:
    def __init__(self) -> None:
        self.nodes: Dict[Tuple[Hub, int], int] = {}
        self.edges: Dict[Tuple[Connection, int], int] = {}

    def reserve_hub(self, hub: Hub, turn: int) -> None:
        self.nodes[(hub, turn)] = self.nodes.get((hub, turn), 0) + 1

    def reserve_conn(self, connection: Connection, turn: int) -> None:
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
            for neighbour in hub.neighbours.keys():
                if neighbour.zone_type == ZoneType.BLOCKED:
                    continue
                new_cost = cost + self.zone_priorities[hub.zone_type]
                if (neighbour not in heuristics
                   or new_cost < heuristics[neighbour]):
                    heuristics[neighbour] = new_cost
                    heapq.heappush(heap, (new_cost, neighbour.name, neighbour))
        if simul.start_hub not in heuristics:
            raise SimulationError(f"End hub is unavailable, map: {simul.name}")
        return heuristics

    def _get_turn_movement(self, turn: int, simul: Simulation) -> str:
        movements = []
        for drone in simul.drones:
            if turn <= 0 or turn >= drone.steps_count:
                continue
            if drone.steps[turn - 1] == drone.steps[turn]:
                continue
            line = f"{drone.id}-{drone.steps[turn].name}"
            movements.append(line)
        return " ".join(movements)

    def show_all_turns(self, simul: Simulation) -> None:
        print(f"\nMap: {simul.name}\n")
        max_turn = simul.analytics.max_turn
        print("\n".join(simul.analytics.turns_output))
        print(f"\nMax turns: {max_turn}")

    def solve(self, simulations: List[Simulation]) -> None:
        for simul in simulations:
            reserv_map = ReservationMap()
            for drone in simul.drones:
                path: List[Hub | Connection] = self._find_path(
                    drone.id, simul, reserv_map)
                drone.steps.extend(path)
                drone.steps_count = len(path)
                for turn, current_loc in enumerate(path[1:-1], 1):
                    if isinstance(current_loc, Connection):
                        reserv_map.reserve_conn(current_loc, turn)
                        reserv_map.reserve_conn(current_loc, turn + 1)
                    else:
                        reserv_map.reserve_hub(current_loc, turn)
                        prev_loc = path[turn - 1]
                        if (prev_loc == current_loc or
                           isinstance(prev_loc, Connection)):
                            continue
                        reserv_map.reserve_conn(
                            current_loc.neighbours[prev_loc], turn)
            simul.analytics = self.get_simul_analytics(simul)

    def get_simul_analytics(self, simul: Simulation) -> Analytics:
        paths: Dict[str, List[Hub | Connection]] = {}
        turns_output: List[str] = []
        drones_count = 0
        for drone in simul.drones:
            paths[drone.id] = drone.steps
            drones_count += 1
        max_turn = max(
            [len(steps) for steps in paths.values()])
        min_turn = min(
            [len(steps) for steps in paths.values()])
        for turn in range(1, max_turn):
            turns_output.append(self._get_turn_movement(turn, simul))
        return Analytics(
            max_turn - 1, min_turn - 1, drones_count, turns_output)

    def _find_path(self,
                   drone_id: str,
                   simul: Simulation,
                   reserv_map: ReservationMap) -> List[Hub | Connection]:
        possible_steps: List[Node] = []
        path: List[Hub | Connection] = []
        heuristics = self._calculate_heuristics(simul)
        first_node = Node(
            location=simul.start_hub,
            turn=0,
            h_cost=heuristics[simul.start_hub])
        heapq.heappush(possible_steps, first_node)
        while possible_steps:
            current_node = heapq.heappop(possible_steps)
            curr_location = current_node.location
            if curr_location.zone_type == ZoneType.RESTRICTED:
                prev_loc = path[-1]
                if isinstance(prev_loc, Hub):
                    path.append(curr_location.neighbours[prev_loc])
            path.append(current_node.location)
            if curr_location == simul.end_hub:
                return path
            possible_steps.clear()
            for neighbour, conn in curr_location.neighbours.items():
                if neighbour.zone_type == ZoneType.BLOCKED:
                    continue
                step_cost = 2 if (
                    neighbour.zone_type == ZoneType.RESTRICTED) else 1
                next_turn = current_node.turn + step_cost
                if neighbour != simul.end_hub:
                    hub_ocup = reserv_map.show_hub_occupancy(
                        neighbour, next_turn)
                    if hub_ocup >= neighbour.max_capacity:
                        continue
                conn_ocup = reserv_map.show_conn_occupancy(
                    conn, current_node.turn + 1)
                if conn_ocup >= conn.max_capacity:
                    continue
                possible_step = Node(
                    neighbour,
                    next_turn,
                    heuristics[neighbour])
                heapq.heappush(possible_steps, possible_step)
            next_ocup = reserv_map.show_hub_occupancy(
                curr_location, current_node.turn + 1
            )
            if (curr_location == simul.start_hub
               or next_ocup <= curr_location.max_capacity):
                wait_step = Node(
                    curr_location,
                    current_node.turn + 1,
                    heuristics[curr_location]
                )
                heapq.heappush(possible_steps, wait_step)
        return []
