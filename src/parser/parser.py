from typing import List
from src.cli import AppConfig
from .models import ParsedElement, ParsedKeyword, ParsedNbDrones
from .errors import ParserError


class MapParser:
    def __init__(self, app: AppConfig) -> None:
        if app is None:
            raise ParserError("AppConfig is None")
        self.app = app

    def __get_parsed_elem(self,
                          line_ind: int,
                          line_els: List[str]) -> ParsedElement:
        first_key = line_els[0]
        if not first_key.endswith(":"):
            raise ParserError(f"First keyword {first_key} must end with ':'."
                              f" Line: {line_ind}")
        try:
            first_token = ParsedKeyword(first_key[:-1])
        except ValueError:
            raise ParserError(f"Unknown map element {line_els[0]}")
        return ParsedNbDrones(ParsedKeyword.NB_DRONES, 1)

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
            parsed_els.append(self.__get_parsed_elem(ind + 1, line_elems))
        if len(parsed_els) == 0:
            raise ParserError("No map elements were found")
        return parsed_els
