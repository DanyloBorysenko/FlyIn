from abc import ABC
from enum import Enum
from typing import Dict
from dataclasses import dataclass


class ParsedKeyword(Enum):
    NB_DRONES = "nb_drones"
    START_HUB = "start_hub"
    END_HUB = "end_hub"
    HUB = "hub"
    CONNECTION = "connection"


class ZoneType(Enum):
    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"


class HubKind(Enum):
    STANDARD = "hub"
    START = "start_hub"
    END = "end_hub"


class ZoneMetaKey(Enum):
    ZONE = "zone"
    COLOR = "color"
    MAX_DRONES = "max_drones"


class ConnectionMetaKey(Enum):
    MAX_LINK_CAP = "max_link_capacity"


class ParsedElement(ABC):
    pass


@dataclass(frozen=True)
class ParsedNbDrones(ParsedElement):
    drones_count: int


@dataclass(frozen=True)
class HubMetadata:
    zone: ZoneType = ZoneType.NORMAL
    color: str = "green"
    max_drones: int = 1


@dataclass(frozen=True)
class ParsedHub(ParsedElement):
    kind: HubKind
    name: str
    coord_x: int
    coord_y: int
    meta: HubMetadata


@dataclass(frozen=True)
class ConnectionMetadata:
    max_link_capacity: int = 1


@dataclass(frozen=True)
class ParsedConnection(ParsedElement):
    zone1: str
    zone2: str
    meta: ConnectionMetadata
