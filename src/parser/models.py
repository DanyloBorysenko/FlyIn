from abc import ABC
from enum import Enum
from dataclasses import dataclass
from src.domain import ZoneType, HubKind
from .errors import ParserError
from typing import Any


class ParsedKeyword(Enum):
    """Define supported map elements."""
    NB_DRONES = "nb_drones"
    START_HUB = "start_hub"
    END_HUB = "end_hub"
    HUB = "hub"
    CONNECTION = "connection"


class ZoneMetaKey(Enum):
    """Define supported zone metadata keys."""
    ZONE = "zone"
    COLOR = "color"
    MAX_DRONES = "max_drones"


class ConnectionMetaKey(Enum):
    """Define supported connection metadata keys."""
    MAX_LINK_CAP = "max_link_capacity"


@dataclass(frozen=True, kw_only=True)
class ParsedElement(ABC):
    """Represent parent class for all parsed map elements."""
    line_ind: int


@dataclass(frozen=True, kw_only=True)
class ParsedNbDrones(ParsedElement):
    """Store information about drones count."""
    drones_count: int

    def __post_init__(self) -> None:
        """
        Check drones count.
        Raise:
            ParserError if total drones count less than 1
        """
        if self.drones_count < 1:
            raise ParserError("drones_count value must be bigger than 0",
                              self.line_ind)


@dataclass(frozen=True, kw_only=True)
class HubMetadata:
    """Store information about hub metadata."""
    line_ind: int
    zone: ZoneType = ZoneType.NORMAL
    color: str | None = None
    max_drones: int = 1

    def __post_init__(self) -> None:
        """
        Check hub metadata.
        Raise:
            ParserError:
            1. max_drones count is less than 0
            2. color is not single-word string
        """
        if self.max_drones < 1:
            raise ParserError("max_drones value must be bigger than 0, "
                              f"was {self.max_drones}", self.line_ind)
        if self.color and not self.color.isalpha():
            raise ParserError("Accepted values for color are any "
                              "valid single-word strings. "
                              f"Actual: '{self.color}'", self.line_ind)


@dataclass(frozen=True, kw_only=True)
class ParsedHub(ParsedElement):
    """Store information about hub."""
    kind: HubKind
    name: str
    coord_x: int
    coord_y: int
    meta: HubMetadata

    def __post_init__(self) -> None:
        """
        Check hub.
        Raise:
            ParserError if zone name contains '-'.
        """
        if "-" in self.name:
            raise ParserError("Zone name can not contain '-'", self.line_ind)


@dataclass(frozen=True, kw_only=True)
class ConnectionMetadata:
    """Store information about connection metadata."""
    line_ind: int
    max_link_capacity: int = 1

    def __post_init__(self) -> None:
        """
        Check connection metadata.
        Raise:
            ParserError if max_link_capacity is less than 1
        """
        if self.max_link_capacity < 1:
            raise ParserError("max_link_capacity value must be bigger than 0, "
                              f"was {self.max_link_capacity}", self.line_ind)


@dataclass(frozen=True, kw_only=True)
class ParsedConnection(ParsedElement):
    """Represent a connection parsed from the input map."""
    zone1: str
    zone2: str
    meta: ConnectionMetadata

    def _zone_set(self) -> frozenset[str]:
        """Return a normalized representation of the connection endpoints."""
        return frozenset((self.zone1, self.zone2))

    def __eq__(self, value: Any) -> bool:
        if not isinstance(value, ParsedConnection):
            return False
        return self._zone_set() == value._zone_set()

    def __hash__(self) -> int:
        return hash(self._zone_set())
