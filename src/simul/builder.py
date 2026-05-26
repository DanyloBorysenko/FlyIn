from src.parser.models import ParsedElement, ParsedHub, ParsedConnection
from src.cli import AppConfig
from .models import SimulationMap, Hub, Connection, Drone
from src.domain import HubKind
from typing import List, Dict


class SimulationBuilder:
    def __init__(self, app: AppConfig) -> None:
        self.app = app

    def _build_hubs(self, data: List[ParsedElement]) -> Dict[str, Hub]:
        hubs = [Hub(el) for el in data if isinstance(el, ParsedHub)]
        return {hub.name: hub for hub in hubs}

    def _build_connections(
            self,
            data: List[ParsedElement],
            hubs: Dict[str, Hub]) -> List[Connection]:
        connections = []
        for el in data:
            if isinstance(el, ParsedConnection):
                conn = Connection(
                    hubs[el.zone1],
                    hubs[el.zone2],
                    el.meta.max_link_capacity)
                connections.append(conn)
        return connections

    def build_sim_map(self, data: List[ParsedElement]) -> SimulationMap:
        hubs: Dict[str, Hub] = self._build_hubs(data)
        connections: Connection = self._build_connections(data, hubs)
        start = [hub for hub in hubs.values() if hub.kind == HubKind.START][0]
        end = [hub for hub in hubs.values() if hub.kind == HubKind.END][0]
        drones = [Drone(i) for i in range(1, data[0].drones_count)]
        return SimulationMap(
            start_hub=start,
            end_hub=end,
            hubs=hubs,
            connections=connections,
            drones=drones)
