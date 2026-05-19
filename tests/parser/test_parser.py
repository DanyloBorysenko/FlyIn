from src.cli import AppConfig
from src.parser import ParsedElement, MapParser, ParserError
import pytest
import os


def test_parser_app_is_none() -> None:
    with pytest.raises(ParserError):
        MapParser(None).parse()


@pytest.fixture
def no_rights_file():
    map_path = "tests/parser/invalid_maps/structure/no_rights.txt"
    original_mode = os.stat(map_path).st_mode
    os.chmod(map_path, 0)
    yield map_path
    os.chmod(map_path, original_mode)


@pytest.mark.parametrize(
        "map_path", [
            "tests/parser/invalid_maps/structure/nonexisted.txt",
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


def test_file_no_rights(no_rights_file: str) -> None:
    app = AppConfig(map_path=no_rights_file)
    with pytest.raises(ParserError):
        MapParser(app=app).parse()


def test_line_with_spaces_only() -> None:
    app = AppConfig(
        map_path="tests/parser/valid_maps/line_with_spaces_only.txt")
    MapParser(app=app).parse()
