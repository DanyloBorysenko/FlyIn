from typing import List, Dict, Set
from src.cli import AppConfig
from src.domain import ZoneType, HubKind
from .models import (ParsedElement, ParsedKeyword, ParsedNbDrones, ParsedHub,
                     ParsedConnection, ZoneMetaKey,
                     ConnectionMetaKey, HubMetadata,
                     ConnectionMetadata)
from .errors import ParserError
from pathlib import Path


class MapParser:
    """Parse map files into validated map elements."""
    def __init__(self, app: AppConfig) -> None:
        self.app = app

    def _parse_nb_drones(self,
                         line_els: List[str],
                         line_ind: int) -> ParsedNbDrones:
        """Parse a drone count declaration."""
        if (len(line_els) < 2):
            raise ParserError("No drones count", line_ind)
        try:
            drones_count = int(line_els[1])
        except ValueError:
            raise ParserError(f"'{line_els[1]}' is not integer",
                              line_ind)
        return ParsedNbDrones(line_ind=line_ind, drones_count=drones_count)

    def _parse_hub(self,
                   line_els: List[str],
                   line_ind: int) -> ParsedElement:
        """Parse a hub declaration."""
        if len(line_els) < 4:
            raise ParserError("Hub needs 4 line elements min. "
                              f"Was {len(line_els)}", line_ind)
        try:
            coord_x = int(line_els[2])
        except ValueError:
            raise ParserError("Coord x must be integer", line_ind)
        try:
            coord_y = int(line_els[3])
        except ValueError:
            raise ParserError("Coord y must be integer", line_ind)
        if len(line_els) > 4:
            meta = self._parse_hub_meta(line_els[4:], line_ind)
        else:
            meta = HubMetadata(line_ind=line_ind)
        return (
                ParsedHub(
                    line_ind=line_ind,
                    kind=HubKind(line_els[0].removesuffix(":")),
                    name=line_els[1],
                    coord_x=coord_x,
                    coord_y=coord_y,
                    meta=meta)
                )

    def _parse_hub_meta(self,
                        meta_els: List[str],
                        line_ind: int) -> HubMetadata:
        """Parse hub metadata."""
        str_meta: Dict[str, str] = self._get_meta_dict(meta_els, line_ind)
        zone_type_val: ZoneType = ZoneType.NORMAL
        color_val: str | None = None
        max_drones_val: int = 1
        for key, val in str_meta.items():
            try:
                zone_meta_key = ZoneMetaKey(key)
            except ValueError:
                raise ParserError(f"Unknown meta key '{key}'",
                                  line_ind)
            if zone_meta_key == ZoneMetaKey.ZONE:
                try:
                    zone_type_val = ZoneType(val)
                except ValueError:
                    raise ParserError(f"Unknown zone type '{val}'",
                                      line_ind)
            elif zone_meta_key == ZoneMetaKey.MAX_DRONES:
                try:
                    max_drones_val = int(val)
                except ValueError:
                    raise ParserError(f"Value '{val}' must be integer.",
                                      line_ind)
            else:
                color_val = val
        return HubMetadata(
            line_ind=line_ind,
            zone=zone_type_val,
            color=color_val,
            max_drones=max_drones_val)

    def _parse_connection(self,
                          line_els: List[str],
                          line_ind: int) -> ParsedElement:
        """Parse a connection declaration."""
        if len(line_els) < 2:
            raise ParserError("Connection needs 2 line elements min. "
                              f"Was {len(line_els)}.", line_ind)
        zone1_zone2: List[str] = line_els[1].split("-")
        if len(zone1_zone2) != 2:
            raise ParserError(f"Wrong connection structure in '{zone1_zone2}'",
                              line_ind)
        if len(line_els) > 2:
            meta = self._parse_connection_meta(line_els[2:], line_ind)
        else:
            meta = ConnectionMetadata(line_ind=line_ind)
        return (ParsedConnection(line_ind=line_ind, zone1=zone1_zone2[0],
                                 zone2=zone1_zone2[1], meta=meta))

    def _parse_connection_meta(self,
                               meta_els: List[str],
                               line_ind: int) -> ConnectionMetadata:
        """Parse connection metadata."""
        str_meta = self._get_meta_dict(meta_els, line_ind)
        capacity = 1
        for key, val in str_meta.items():
            try:
                ConnectionMetaKey(key)
            except ValueError:
                raise ParserError(f"Unknown meta key '{key}'.",
                                  line_ind)
            try:
                capacity = int(val)
            except ValueError:
                raise ParserError(f"Value for the key {key} "
                                  f"must be integer, but was {val}.",
                                  line_ind)
        return ConnectionMetadata(
            line_ind=line_ind,
            max_link_capacity=capacity)

    def _get_meta_dict(self, meta_els: List[str],
                       line_ind: int) -> Dict[str, str]:
        """
        Parse metadata tokens into a key-value dictionary.

        Raises:
            ParserError: If the metadata syntax is invalid.
        """
        if not meta_els[0].startswith("["):
            raise ParserError("Metadata must start with '['.", line_ind)
        if not meta_els[-1].endswith("]"):
            raise ParserError("Metadata must end with ']'.", line_ind)
        meta_els = meta_els.copy()
        meta_els[0] = meta_els[0].removeprefix("[")
        meta_els[-1] = meta_els[-1].removesuffix("]")
        meta = {}
        for el in meta_els:
            key_val = el.split("=")
            if len(key_val) != 2:
                raise ParserError(f"Wrong meta syntax in '{el}'.", line_ind)
            if key_val[0] in meta:
                raise ParserError(f"Duplicate meta key '{key_val[0]}'.",
                                  line_ind)
            meta[key_val[0]] = key_val[1]
        return meta

    def _get_parsed_keyword(self,
                            line_ind: int,
                            line_els: List[str]) -> ParsedElement:
        """
        Call appropriate parsing function depending on first line token
        Args:
            line_ind: index of the line
            line_els: list of words from the line, that was splited by space.
        Returns:
            ParsedElement
        Raises:
            ParserError:
                If the first word of the line does not have ':' in the end.
                If the first word of the line is not defined in ParsedKeyword
        """
        first_key = line_els[0]
        if not first_key.endswith(":"):
            raise ParserError(f"First keyword '{first_key}' must end with ':'",
                              line_ind
                              )
        helpers = {
            ParsedKeyword.NB_DRONES: self._parse_nb_drones,
            ParsedKeyword.HUB: self._parse_hub,
            ParsedKeyword.START_HUB: self._parse_hub,
            ParsedKeyword.END_HUB: self._parse_hub,
            ParsedKeyword.CONNECTION: self._parse_connection,
        }
        try:
            first_token = ParsedKeyword(first_key[:-1])
            parsed_el = helpers[first_token](line_els, line_ind)
            return parsed_el
        except ValueError:
            raise ParserError(f"Unknown map element '{first_key}'", line_ind)

    def _raise_unknown_zone(self, zone_name: str, line_ind: int) -> None:
        raise ParserError(f"Unknown zone - {zone_name}. "
                          "Connections must link only previously "
                          "defined zones", line_ind)

    def _validate(self, parsed_els: List[ParsedElement]) -> None:
        """
        Validate parsed map elements.

        Ensure the map contains exactly one start hub and one end hub,
        that hub names are unique, and that all connections reference
        previously defined hubs.
        Raise:
            ParserError
        """
        if not isinstance(parsed_els[0], ParsedNbDrones):
            raise ParserError("First map element must be nb_drones", 0)
        hubs: Dict[str, ParsedElement] = {}
        connections: Set[ParsedConnection] = set()
        start_hubs = 0
        end_hubs = 0
        for el in parsed_els[1:]:
            if isinstance(el, ParsedHub):
                if el.name in hubs:
                    raise ParserError(f"Hub name duplication - '{el.name}'",
                                      el.line_ind)
                match el.kind:
                    case HubKind.START:
                        start_hubs += 1
                    case HubKind.END:
                        end_hubs += 1
                hubs[el.name] = el
            elif isinstance(el, ParsedConnection):
                if el in connections:
                    raise ParserError("Connection duplication", el.line_ind)
                if el.zone1 not in hubs:
                    self._raise_unknown_zone(el.zone1, el.line_ind)
                if el.zone2 not in hubs:
                    self._raise_unknown_zone(el.zone2, el.line_ind)
                connections.add(el)
        if start_hubs != 1:
            raise ParserError("Expected exactly 1 start_hub, "
                              f"got {start_hubs}")
        if end_hubs != 1:
            raise ParserError("Expected exactly 1 end_hub, "
                              f"got {end_hubs}")

    def parse_map(self, map_path: str) -> List[ParsedElement]:
        """
        Parse and validate a map file.
        Args:
            map_path: Path to the map file.
        Returns:
            Parsed map elements in file order.
        Raises:
            ParserError: If the file cannot be read, parsed, or validated.
        """
        try:
            with open(map_path, "r") as f:
                lines = f.readlines()
        except FileNotFoundError:
            raise ParserError(f"File '{self.app.map_path}' doesn't exist")
        except PermissionError:
            raise ParserError("No reading permission for file "
                              f"'{map_path}'")
        parsed_els: List[ParsedElement] = []
        for ind, line in enumerate(lines):
            if line.startswith("#") or line == "\n":
                continue
            line_elems = line.split()
            if len(line_elems) == 0:
                continue
            parsed_els.append(self._get_parsed_keyword(ind + 1, line_elems))
        if len(parsed_els) == 0:
            raise ParserError("No map elements were found")
        self._validate(parsed_els)
        return parsed_els

    def parse_maps(
            self,
            root_path: str) -> Dict[str, List[ParsedElement]]:
        """
        Parse all maps in the configured playlist.
        Args:
            root_path: Root directory containing map files.
        Returns:
            Mapping of file paths to parsed map elements.
        Raises:
            ParserError: If a map or directory cannot be processed.
        """
        root = Path(root_path)
        map_provided = Path(self.app.map_path)
        if not map_provided.exists():
            raise ParserError(f"file '{map_provided}' doesn't exist")
        if not root.exists():
            raise ParserError(f"dir '{root}' doesn't exist")
        maps: Dict[str, List[ParsedElement]] = {}
        playlist = root.rglob("*")
        if root not in map_provided.parents:
            maps.update({str(map_provided): self.parse_map(str(map_provided))})
        order = {
            "easy": 1,
            "medium": 2,
            "hard": 3,
            "challenger": 4
        }
        files = [file for file in playlist if file.is_file()]
        sorted_files = sorted(files, key=lambda f: (
            order.get(f.parent.name, 0),
            f.name)
            )
        for map_file in sorted_files:
            name = str(map_file)
            try:
                maps[name] = self.parse_map(name)
            except ParserError as e:
                raise ParserError(f"{e}, file name: {name}")
        if self.app.debug:
            for name, els in maps.items():
                print(f"\nMap: '{name}' was parsed."
                      f"\nResult:\n{"\n".join([str(el) for el in els])}")
        return maps
