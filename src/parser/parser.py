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
    def __init__(self, app: AppConfig) -> None:
        self.app = app

    def _parse_nb_drones(self,
                         line_els: List[str],
                         line_ind: int) -> ParsedNbDrones:
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
        str_meta: Dict[str, str] = self._get_meta_dict(meta_els, line_ind)
        meta = {"line_ind": line_ind}
        for key, val in str_meta.items():
            try:
                key = ZoneMetaKey(key)
            except ValueError:
                raise ParserError(f"Unknown meta key '{key}'",
                                  line_ind)
            if key == ZoneMetaKey.ZONE:
                try:
                    val = ZoneType(val)
                except ValueError:
                    raise ParserError(f"Unknown zone type '{val}'",
                                      line_ind)
            elif key == ZoneMetaKey.MAX_DRONES:
                try:
                    val = int(val)
                except ValueError:
                    raise ParserError(f"Value '{val}' must be integer.",
                                      line_ind)
            meta[key.value] = val
        return HubMetadata(**meta)

    def _parse_connection(self,
                          line_els: List[str],
                          line_ind: int) -> ParsedElement:
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
        str_meta = self._get_meta_dict(meta_els, line_ind)
        meta = {"line_ind": line_ind}
        for key, val in str_meta.items():
            try:
                key = ConnectionMetaKey(key)
            except ValueError:
                raise ParserError(f"Unknown meta key '{key}'.",
                                  line_ind)
            try:
                val = int(val)
            except ValueError:
                raise ParserError(f"Value for the key {key.value} "
                                  f"must be integer, but was {val}.",
                                  line_ind)
            meta[key.value] = val
        return ConnectionMetadata(**meta)

    def _get_meta_dict(self, meta_els: List[str],
                       line_ind: int) -> Dict[str, str]:
        if not meta_els[0].startswith("["):
            raise ParserError("Metadata must start with '['.", line_ind)
        if not meta_els[-1].endswith("]"):
            raise ParserError("Metadata must end with ']'.", line_ind)
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
            if self.app.debug:
                print(f"Element was parsed: {parsed_el}")
            return parsed_el
        except ValueError:
            raise ParserError(f"Unknown map element '{first_key}'", line_ind)

    def _raise_unknown_zone(self, zone_name: str, line_ind: int) -> None:
        raise ParserError(f"Unknown zone - {zone_name}. "
                          "Connections must link only previously "
                          "defined zones", line_ind)

    def _validate(self, parsed_els: List[ParsedElement]) -> None:
        if not isinstance(parsed_els[0], ParsedNbDrones):
            raise ParserError("First map element must be nb_drones", 0)
        hubs: Dict[str: ParsedElement] = {}
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
        try:
            with open(map_path, "r") as f:
                lines = f.readlines()
                if self.app.debug:
                    print(f"File '{map_path}' was read")
                    print(f"\nLines: {lines}\n")
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
        root = Path(root_path)
        map_provided = Path(self.app.map_path)
        if not map_provided.exists():
            raise ParserError(f"file '{map_provided}' doesn't exist")
        if not root.exists():
            raise ParserError(f"dir '{root}' doesn't exist")
        playlist = root.rglob("*")
        if root not in map_provided.parents:
            return {map_provided: self.parse_map(map_provided)}
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
        maps: Dict[str, List[ParsedElement]] = {}
        for map_file in sorted_files:
            name = str(map_file)
            try:
                maps[name] = self.parse_map(name)
            except ParserError as e:
                raise ParserError(f"{e}, file name: {name}")
        return maps
