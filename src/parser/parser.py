from typing import List
from src.cli import AppConfig
from .models import ParsedElement, ParsedKeyword, ParsedNbDrones
from .errors import ParserError


class MapParser:
    def __init__(self, app: AppConfig) -> None:
        if app is None:
            raise ParserError("AppConfig is None")
        self.app = app

    def __get_parsed_elem(self, line_ind: int, line: str) -> ParsedElement:
        line_els = line.split(" ")
        try:
            first_token = ParsedKeyword(line_els[0])
            print(first_token)
        except ValueError:
            raise ParserError(f"Unknown map element {line_els[0]}")
        return ParsedNbDrones(ParsedKeyword.NB_DRONES)

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
            if line.startswith("#"):
                continue
            parsed_els.append(self.__get_parsed_elem(ind, line))
        return parsed_els
    
