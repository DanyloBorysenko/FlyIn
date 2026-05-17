from src.cli import AppConfig
from src.parser import ParsedElement, MapParser, ParserError
import pytest


def test_parser_appIsNone() -> None:
    with pytest.raises(ParserError):
        MapParser(None).parse


@pytest.mark.parametrize(
        "map_path", [
            "tests/parser/invalid_maps/structure/nonexisted.txt",
            "tests/parser/invalid_maps/structure/no_rights.txt",
            "tests/parser/invalid_maps/structure/no_start.txt",
            "tests/parser/invalid_maps/structure/no_end.txt",
            "tests/parser/invalid_maps/structure/no_nb_drones.txt",
            "tests/parser/invalid_maps/structure/empty.txt",
            "tests/parser/invalid_maps/structure/dup_start_end.txt"
        ]
)
def test_invalid_struct_maps(map_path: str) -> None:
    app = AppConfig(map_path=map_path)

    with pytest.raises(ParserError):
        MapParser(app=app).parse()
