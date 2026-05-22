from abc import ABC
from enum import Enum
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

    def __post_init__(self) -> None:
        if self.drones_count < 1:
            raise ValueError("drones_count value must be bigger than 0")


@dataclass(frozen=True)
class HubMetadata:
    zone: ZoneType = ZoneType.NORMAL
    color: str | None = None
    max_drones: int = 1

    def __post_init__(self) -> None:
        if self.max_drones < 1:
            raise ValueError("max_drones value must be bigger than 0, "
                             f"was {self.max_drones}")
        if self.color and not self.color.isalpha():
            raise ValueError("Accepted values for color are any "
                             "valid single-word strings."
                             f"Actual: {self.color}")


@dataclass(frozen=True)
class ParsedHub(ParsedElement):
    kind: HubKind
    name: str
    coord_x: int
    coord_y: int
    meta: HubMetadata

    def __post_init__(self) -> None:
        if "-" in self.name:
            raise ValueError("Zone name can not contain '-'")
        # if self.coord_x < 0:
        #     raise ValueError("coord_x can not be negative")
        # if self.coord_y < 0:
        #     raise ValueError("coord_y can not be negative")


@dataclass(frozen=True)
class ConnectionMetadata:
    max_link_capacity: int = 1

    def __post_init__(self) -> None:
        if self.max_link_capacity < 1:
            raise ValueError("max_link_capacity value must be bigger than 0, "
                             f"was {self.max_link_capacity}")


@dataclass(frozen=True)
class ParsedConnection(ParsedElement):
    zone1: str
    zone2: str
    meta: ConnectionMetadata
