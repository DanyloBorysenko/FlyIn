from abc import ABC
from enum import Enum
from dataclasses import dataclass
from .errors import ParserError


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


@dataclass(frozen=True, kw_only=True)
class ParsedElement(ABC):
    line_ind: int


@dataclass(frozen=True, kw_only=True)
class ParsedNbDrones(ParsedElement):
    drones_count: int

    def __post_init__(self) -> None:
        if self.drones_count < 1:
            raise ParserError("drones_count value must be bigger than 0",
                              self.line_ind)


@dataclass(frozen=True, kw_only=True)
class HubMetadata(ParsedElement):
    zone: ZoneType = ZoneType.NORMAL
    color: str | None = None
    max_drones: int = 1

    def __post_init__(self) -> None:
        if self.max_drones < 1:
            raise ParserError("max_drones value must be bigger than 0, "
                              f"was {self.max_drones}", self.line_ind)
        if self.color and not self.color.isalpha():
            raise ParserError("Accepted values for color are any "
                              "valid single-word strings. "
                              f"Actual: '{self.color}'", self.line_ind)


@dataclass(frozen=True, kw_only=True)
class ParsedHub(ParsedElement):
    kind: HubKind
    name: str
    coord_x: int
    coord_y: int
    meta: HubMetadata

    def __post_init__(self) -> None:
        if "-" in self.name:
            raise ParserError("Zone name can not contain '-'", self.line_ind)
        # if self.coord_x < 0:
        #     raise ValueError("coord_x can not be negative")
        # if self.coord_y < 0:
        #     raise ValueError("coord_y can not be negative")


@dataclass(frozen=True)
class ConnectionMetadata(ParsedElement):
    max_link_capacity: int = 1

    def __post_init__(self) -> None:
        if self.max_link_capacity < 1:
            raise ParserError("max_link_capacity value must be bigger than 0, "
                              f"was {self.max_link_capacity}", self.line_ind)


@dataclass(frozen=True, kw_only=True)
class ParsedConnection(ParsedElement):
    zone1: str
    zone2: str
    meta: ConnectionMetadata

    def _zone_set(self) -> frozenset[str]:
        return frozenset((self.zone1, self.zone2))

    def __eq__(self, value):
        if not isinstance(value, ParsedConnection):
            return False
        return self._zone_set() == value._zone_set()

    def __hash__(self):
        return hash(self._zone_set())
