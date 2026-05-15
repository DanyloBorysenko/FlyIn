from typing import List
from src.cli import AppConfig
from .models import ParsedElement
from .errors import ParserError


class MapParser:
    def __init__(self, app: AppConfig) -> None:
        self.app = app

    def parse(self) -> List[ParsedElement]:
        try:
            with open(self.app.map_path, "r") as f:
                lines = f.readlines()
                print(lines)
        except FileNotFoundError:
            raise ParserError(f"File '{self.app.map_path}' is not exist")
        return []
