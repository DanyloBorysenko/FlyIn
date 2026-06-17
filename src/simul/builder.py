from src.parser.models import (ParsedElement, ParsedHub,
                               ParsedConnection, ParsedNbDrones)
from src.cli import AppConfig
from .models import Simulation, Hub, Connection, Drone, Analytics
from src.domain import HubKind
from typing import List, Dict
from .errors import SimulationError

MAX_DRONES_COUNT = 100


class SimulationBuilder:
    """Create simulations from parsed elements"""
    def __init__(self, app: AppConfig) -> None:
        self.app = app

    def _build_hubs(self, data: List[ParsedElement]) -> Dict[str, Hub]:
        """
        Build hubs from parsed elements.

        Return:
            Mapping of hub names to created Hub objects.
        """
        hubs = [Hub(el) for el in data if isinstance(el, ParsedHub)]
        return {hub.name: hub for hub in hubs}

    def _build_connections(
            self,
            data: List[ParsedElement],
            hubs: Dict[str, Hub]) -> Dict[str, Connection]:
        """
        Build connections from parsed elements.
        Insert created connections to appropriate hubs.

        Args:
            data: total parsed elements from a map file
            hubs: created hub objects dict

        Return:
            Mapping of connection names to created Connection objects.
        """
        connections = {}
        for el in data:
            if isinstance(el, ParsedConnection):
                hub1 = hubs[el.zone1]
                hub2 = hubs[el.zone2]
                conn = Connection(hub1, hub2, el.meta.max_link_capacity)
                hub1.neighbours.update({hub2: conn})
                hub2.neighbours.update({hub1: conn})
                connections[conn.name] = conn
        return connections

    def build_simulation(self,
                         map_name: str,
                         parsed_els: List[ParsedElement]) -> Simulation:
        """
        Build Simulation object from parsed elements

        Raise:
            SimulationError:
            If first parsed element does not have drones count.
            If drones count is bigger than the maximum
        """
        hubs: Dict[str, Hub] = self._build_hubs(parsed_els)
        connections: Dict[str, Connection] = self._build_connections(
            parsed_els, hubs)
        start = [hub for hub in hubs.values() if hub.kind == HubKind.START][0]
        end = [hub for hub in hubs.values() if hub.kind == HubKind.END][0]
        if not isinstance(parsed_els[0], ParsedNbDrones):
            raise SimulationError("First parsed element must be instance of "
                                  "ParsedNbDrones class")
        nb_drones = parsed_els[0].drones_count
        if nb_drones > MAX_DRONES_COUNT:
            raise SimulationError(f"Too much drones, map: {map_name}")
        start.max_capacity = nb_drones
        end.max_capacity = nb_drones
        drones = [Drone(i) for i in range(1, nb_drones + 1)]
        simul = Simulation(
            name=map_name,
            start_hub=start,
            end_hub=end,
            hubs=hubs,
            connections=connections,
            drones=drones,
            analytics=Analytics())
        if self.app.debug:
            print(f"Simul was built: {simul}")
        return simul

    def build_simul_map(
            self,
            parsed_maps: Dict[str, List[ParsedElement]]
            ) -> List[Simulation]:
        simulations: List[Simulation] = list()
        first_simul = self.build_simulation(
            self.app.map_path, parsed_maps.pop(self.app.map_path))
        simulations.append(first_simul)
        for map_name, parsed_els in parsed_maps.items():
            simulations.append(self.build_simulation(map_name, parsed_els))
        return simulations
