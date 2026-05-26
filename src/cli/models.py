from dataclasses import dataclass
from enum import Enum


class Flag(Enum):
    MAP_PATH = "--map-path"
    DEBUG = "--debug"
    VISUAL = "--visual"

    def parse_flag(self) -> str:
        return self.value.removeprefix("--").replace("-", "_")

    @staticmethod
    def show_flags() -> str:
        return ", ".join(flag.value for flag in Flag)


@dataclass
class AppConfig:
    map_path: str = "maps/easy/01_linear_path.txt"
    debug: bool = False
    visual: bool = False
