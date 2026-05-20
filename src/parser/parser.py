from typing import List, Dict
from src.cli import AppConfig
from .models import ParsedElement, ParsedKeyword, ParsedNbDrones, ParsedHub, ParsedConnection, ZoneType, ZoneMetaKey
from .errors import ParserError


class MapParser:
    def __init__(self, app: AppConfig) -> None:
        self.app = app

    def _parse_nb_drones(self,
                         line_els: List[str],
                         line_ind: int) -> ParsedNbDrones:
        if (len(line_els) < 2):
            raise ParserError(f"No drones count. Line: {line_ind}")
        try:
            return ParsedNbDrones(int(line_els[1]))
        except ValueError:
            raise ParserError(f"'{line_els[1]}' is not integer. "
                              f"Line: {line_ind}")

    def _parse_hub(self,
                   kind: ParsedKeyword,
                   line_els: List[str],
                   line_ind: int) -> ParsedElement:
        if len(line_els) < 4:
            raise ParserError("Hub needs 4 line elements min. "
                              f"Was {len(line_els)} Line: {line_ind}")
        try:
            coord_x = int(line_els[2])
        except ValueError:
            raise ParserError(f"Coord x must be integer. Line: {line_ind}")
        try:
            coord_y = int(line_els[3])
        except ValueError:
            raise ParserError(f"Coord y must be integer. Line: {line_ind}")
        meta: Dict = None if len(line_els) == 4 else self._parse_hub_meta(line_els[4:], line_ind)
        if meta and ZoneMetaKey.ZONE in meta:
            zone_type = meta[ZoneMetaKey.ZONE]
        else:
            zone_type = ZoneType.NORMAL
        return (
            ParsedHub(
                kind=kind,
                name=line_els[1],
                coord_x=coord_x,
                coord_y=coord_y,
                zone_type=zone_type,
                metadata=meta)
                )

    def _parse_connection(self,
                          line_els: List[str],
                          line_ind: int) -> ParsedElement:
        return (ParsedConnection("zone1", "zone2", {}))

    def _parse_hub_meta(self, meta_els: List[str], line_ind: int) -> Dict:
        if not meta_els[0].startswith("["):
            raise ParserError("Metadata must start with '['. "
                              f"Line: {line_ind}")
        if not meta_els[-1].endswith("]"):
            raise ParserError("Metadata must end with ']'. "
                              f"Line: {line_ind}")
        meta = {}
        for el in meta_els:
            key_val: List[str] = el.split("=")
            if len(key_val) != 2:
                raise ParserError(f"Wrong meta structure in '{el}'. "
                                  f"Line: {line_ind}")
            try:
                key = ZoneMetaKey(key_val[0][1:])
            except ValueError:
                raise ParserError(f"Unknown meta key '{key_val[0]}'. "
                                  f"Line: {line_ind}")
            if key == ZoneMetaKey.ZONE:
                try:
                    val = ZoneType(key_val[1])
                except ValueError:
                    raise ParserError(f"Unknown zone type '{key_val[1]}'. "
                                      f"Line: {line_ind}")
            elif key == ZoneMetaKey.MAX_DRONES:
                try:
                    val = int(key_val[1])
                except ValueError:
                    raise ParserError(f"Value '{key_val[1]}' must be integer. "
                                      f"Line: {line_ind}")
            else:
                val = key_val[1]
            if key in meta:
                raise ParserError(f"Duplicate meta key '{key}'. "
                                  f"Line: {line_ind}")
            meta[key] = val
        return meta

    def _get_parsed_keyword(self,
                            line_ind: int,
                            line_els: List[str]) -> ParsedElement:
        first_key = line_els[0]
        if not first_key.endswith(":"):
            raise ParserError(f"First keyword {first_key} must end with ':'."
                              f" Line: {line_ind}")
        try:
            first_token = ParsedKeyword(first_key[:-1])
            if first_token == ParsedKeyword.NB_DRONES:
                parsed_el = self._parse_nb_drones(line_els, line_ind)
            elif first_token in [ParsedKeyword.HUB, ParsedKeyword.START_HUB, ParsedKeyword.END_HUB]:
                parsed_el = self._parse_hub(first_token, line_els, line_ind)
            elif first_token == ParsedKeyword.CONNECTION:
                parsed_el = self._parse_connection(line_els, line_ind)
            return parsed_el
        except ValueError:
            raise ParserError(f"Unknown map element {line_els[0]}")

    def parse(self) -> List[ParsedElement]:
        try:
            with open(self.app.map_path, "r") as f:
                lines = f.readlines()
                if self.app.debug:
                    print(f"File '{self.app.map_path}' was read")
                    print(lines)
        except FileNotFoundError:
            raise ParserError(f"File '{self.app.map_path}' is not exist")
        except PermissionError:
            raise ParserError("No reading permission for file "
                              f"'{self.app.map_path}'")
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
        return parsed_els
