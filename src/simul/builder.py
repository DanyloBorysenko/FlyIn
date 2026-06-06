from src.parser.models import ParsedElement, ParsedHub, ParsedConnection
from src.cli import AppConfig
from .models import Simulation, Hub, Connection, Drone
from src.domain import HubKind
from typing import List, Dict


class SimulationBuilder:
    def __init__(self,
                 app: AppConfig,
                 parsed_maps: Dict[str, List[ParsedElement]]) -> None:
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

    def build_simulation(self, data: List[ParsedElement]) -> Simulation:
        hubs: Dict[str, Hub] = self._build_hubs(data)
        connections: Dict[str, Connection] = self._build_connections(
            data, hubs)
        start = [hub for hub in hubs.values() if hub.kind == HubKind.START][0]
        end = [hub for hub in hubs.values() if hub.kind == HubKind.END][0]
        start.max_capacity = data[0].drones_count
        end.max_capacity = data[0].drones_count
        drones = [Drone(i) for i in range(1, data[0].drones_count + 1)]
        return Simulation(
            start_hub=start,
            end_hub=end,
            hubs=hubs,
            connections=connections,
            drones=drones)
