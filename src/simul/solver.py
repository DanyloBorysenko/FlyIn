from typing import Dict, Tuple, List
from .models import Hub, Connection, Simulation, Node, Analytics
from src.domain import ZoneType
from .errors import SimulationError
from src.cli import AppConfig
import heapq


class ReservationMap:
    """
    Store information about every location on every turn
    with actual number of drones.
    Serves as a verification point for solver.
    """
    def __init__(self) -> None:
        """
        Create separate reservation storages for zone and connections.
        """
        self.nodes: Dict[Tuple[Hub, int], int] = {}
        self.edges: Dict[Tuple[Connection, int], int] = {}

    def reserve_hub(self, hub: Hub, turn: int) -> None:
        """Reserve hub on appropriate turn, increse actual drones count"""
        self.nodes[(hub, turn)] = self.nodes.get((hub, turn), 0) + 1

    def reserve_conn(self, connection: Connection, turn: int) -> None:
        """
        Reserve connection on appropriate turn,
        increse actual drones count
        """
        self.edges[(connection, turn)] = self.edges.get(
            (connection, turn), 0) + 1

    def show_hub_occupancy(self, hub: Hub, turn: int) -> int:
        """Give actual drones count in received hub during received turn"""
        return self.nodes.get((hub, turn), 0)

    def show_conn_occupancy(self, connection: Connection, turn: int) -> int:
        """Give actual drones count in received connection
        during received turn
        """
        return self.edges.get((connection, turn), 0)


class Solver:
    """Find the best path for every drone and update simulations"""
    def __init__(self, app: AppConfig) -> None:
        """
        Initialized solver instance and define zone priorities.
        Zone priorities will be used only for heuristic calculations.
        Zone with lower priority value will be prioritized.
        """
        self.zone_priorities = {
            ZoneType.NORMAL: 1.0,
            ZoneType.RESTRICTED: 2.0,
            ZoneType.PRIORITY: 0.9
        }
        self.app = app

    def _calculate_heuristics(self, simul: Simulation) -> Dict[Hub, float]:
        """
        Calculate the minimum cost to reach the end hub from each hub.
        Args:
            simul: Simulation for which the costs are computed.
        Returns:
            Mapping of hubs to the minimum cost required to reach the end hub.
        Raises:
            SimulationError: If the end hub is unreachable.
        """
        end = simul.end_hub
        heuristics = {end: 0.0}
        heap = [(0.0, end.name, end)]
        while heap:
            cost, _, hub = heapq.heappop(heap)
            for neighbour in hub.neighbours.keys():
                if neighbour.zone_type == ZoneType.BLOCKED:
                    continue
                new_cost = cost + self.zone_priorities[neighbour.zone_type]
                if (neighbour not in heuristics
                   or new_cost < heuristics[neighbour]):
                    heuristics[neighbour] = new_cost
                    heapq.heappush(heap, (new_cost, neighbour.name, neighbour))
        if simul.start_hub not in heuristics:
            raise SimulationError(f"End hub is unavailable, map: {simul.name}")
        return heuristics

    def _get_turn_movement(self, turn: int, simul: Simulation) -> str:
        """Forme output line that represents one turn"""
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
        """Display information about received simulation"""
        print(f"\nMap: {simul.name}\n")
        print("\n".join(simul.analytics.turns_output))
        max_turn = simul.analytics.max_turn
        print(f"\nMax turns: {max_turn}")

    def solve(self, simulations: List[Simulation]) -> None:
        """
        For every simulation iterate over all drones
        and finds the best path for every drone.
        Finded path will be inserted in drone's steps.
        Updates reservation map and create Analitics object.
        """
        for simul in simulations:
            reserv_map = ReservationMap()
            heuristics = self._calculate_heuristics(simul)
            for drone in simul.drones:
                path: List[Hub | Connection] = self._find_path(
                    drone.id, simul, reserv_map, heuristics)
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

    def get_simul_analytics(
            self, simul: Simulation) -> Analytics:
        """
        Create Analitics object that store information about
        current simulation.
        Contains:
            the maximum number of steps needed to achieve an end zone
            the minimum number of steps needed to achieve
            drones count
            list of turns movement, used for an output
        """
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
            turns_output.append(
                self._get_turn_movement(turn, simul))
        return Analytics(
            max_turn - 1, min_turn - 1, drones_count, turns_output)

    def _find_path(self,
                   drone_id: str,
                   simul: Simulation,
                   reserv_map: ReservationMap,
                   heuristics: Dict[Hub, float]) -> List[Hub | Connection]:
        """
        Find a valid path to the destination hub.

        Use the heuristic map and current reservations to select
        a route for the specified drone.
        """
        possible_steps: List[Node] = []
        path: List[Hub | Connection] = []
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
                if self.app.debug:
                    print(f"Dron {drone_id}, path was found: {path}")
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
