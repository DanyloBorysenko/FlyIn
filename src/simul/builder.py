from src.parser.models import (ParsedElement, ParsedHub,
                               ParsedConnection, ParsedNbDrones)
from src.cli import AppConfig
from .models import Simulation, Hub, Connection, Drone, Analytics
from src.domain import HubKind
from typing import List, Dict
from .errors import SimulationError


class SimulationBuilder:
    def __init__(self, app: AppConfig) -> None:
        self.app = app

    def _build_hubs(self, data: List[ParsedElement]) -> Dict[str, Hub]:
        hubs = [Hub(el) for el in data if isinstance(el, ParsedHub)]
        return {hub.name: hub for hub in hubs}

    def _build_connections(
            self,
            data: List[ParsedElement],
            hubs: Dict[str, Hub]) -> Dict[str, Connection]:
        connections = {}
        for el in data:
            if isinstance(el, ParsedConnection):
                conn = Connection(
                    hubs[el.zone1],
                    hubs[el.zone2],
                    el.meta.max_link_capacity)
                hubs[conn.hub_1.name].connections.append(conn)
                hubs[conn.hub_2.name].connections.append(conn)
                connections[conn.name] = conn
        return connections

    def build_simulation(self,
                         map_name: str,
                         parsed_els: List[ParsedElement]) -> Simulation:
        hubs: Dict[str, Hub] = self._build_hubs(parsed_els)
        connections: Dict[str, Connection] = self._build_connections(
            parsed_els, hubs)
        start = [hub for hub in hubs.values() if hub.kind == HubKind.START][0]
        end = [hub for hub in hubs.values() if hub.kind == HubKind.END][0]
        if not isinstance(parsed_els[0], ParsedNbDrones):
            raise SimulationError("First parsed element must be instance of "
                                  "ParsedNbDrones class")
        nb_drones = parsed_els[0].drones_count
        start.max_capacity = nb_drones
        end.max_capacity = nb_drones
        drones = [Drone(i) for i in range(1, nb_drones + 1)]
        return Simulation(
            name=map_name,
            start_hub=start,
            end_hub=end,
            hubs=hubs,
            connections=connections,
            drones=drones,
            analytics=Analytics())

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
