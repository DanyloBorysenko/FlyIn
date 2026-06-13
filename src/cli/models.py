from dataclasses import dataclass
from enum import Enum


class Flag(Enum):
    """Define the command-line flags supported by the application."""
    MAP_PATH = "--map-path"
    PLAYLIST_PATH = "--playlist-path"
    DEBUG = "--debug"
    VISUAL = "--visual"

    def parse_flag(self) -> str:
        """Convert a flag name to the corresponding AppConfig attribute."""
        return self.value.removeprefix("--").replace("-", "_")

    @staticmethod
    def show_flags() -> str:
        """Return a comma-separated list of all supported flags."""
        return ", ".join(flag.value for flag in Flag)


@dataclass
class AppConfig:
    """Store application configuration derived from command-line arguments."""
    map_path: str = "maps/easy/01_linear_path.txt"
    playlist_path: str = "maps"
    debug: bool = False
    visual: bool = False
