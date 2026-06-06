from src.cli import AppConfig
from src.parser import MapParser, ParserError
from pathlib import Path
import pytest
import os

INVLD_SYNTX_MAPS = Path("tests/parser/invalid_maps/syntax").glob("*.txt")
INVLD_SEMNTC_MAPS = Path("tests/parser/invalid_maps/semantic").glob("*.txt")


@pytest.fixture
def no_rights_file():
    map_path = "tests/parser/invalid_maps/structure/no_rights.txt"
    original_mode = os.stat(map_path).st_mode
    os.chmod(map_path, 0)
    yield map_path
    os.chmod(map_path, original_mode)


def test_empty_file() -> None:
    with pytest.raises(ParserError):
        MapParser(
            AppConfig("tests/parser/invalid_maps/structure/empty.txt")
            ).parse_map("tests/parser/invalid_maps/structure/empty.txt")


def test_file_not_exists() -> None:
    with pytest.raises(ParserError):
        MapParser(
            AppConfig("tests/parser/invalid_maps/structure/nonexisted.txt")
            ).parse_map("tests/parser/invalid_maps/structure/empty.txt")


def test_file_no_rights(no_rights_file: str) -> None:
    app = AppConfig(map_path=no_rights_file)
    with pytest.raises(ParserError):
        MapParser(app=app).parse_map(
            "tests/parser/invalid_maps/structure/no_rights.txt")


@pytest.mark.parametrize("map_path", INVLD_SYNTX_MAPS,
                         ids=lambda path: path.stem)
def test_invalid_syntax_maps(map_path: Path) -> None:
    with pytest.raises(ParserError):
        app = AppConfig(map_path=str(map_path))
        MapParser(app=app).parse_map(map_path)


@pytest.mark.parametrize("map_path", INVLD_SEMNTC_MAPS,
                         ids=lambda path: path.stem)
def test_invalid_semantic_maps(map_path: Path) -> None:
    with pytest.raises(ParserError):
        app = AppConfig(map_path=str(map_path))
        MapParser(app=app).parse_map(map_path)
