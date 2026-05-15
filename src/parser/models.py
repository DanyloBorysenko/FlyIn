from abc import ABC
from enum import Enum
from typing import Dict, Literal
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


class ZoneMeta(Enum):
    ZONE = "zone"
    COLOR = "color"
    MAX_DRONES = "max_drones"


class ConnectionMeta(Enum):
    MAX_LINK_CAP = "max_link_capacity"


class ParsedElement(ABC):
    pass


@dataclass
class ParsedNbDrones(ParsedElement):
    kind: ParsedKeyword.NB_DRONES
    drones_count: int


@dataclass(frozen=True)
class ParsedHub(ParsedElement):
    kind: Literal[ParsedKeyword.HUB,
                  ParsedKeyword.START_HUB,
                  ParsedKeyword.END_HUB]
    name: str
    coord_x: int
    coord_y: int
    type: ZoneType
    metadata: Dict[ZoneMeta, str]


@dataclass(frozen=True)
class ParsedConnection(ParsedElement):
    kind: ParsedKeyword.CONNECTION
    zone1: str
    zone2: str
    metadata: Dict[ConnectionMeta, str]
