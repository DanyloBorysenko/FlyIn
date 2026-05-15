from src.cli import AppConfig
from src.parser import ParsedElement, MapParser, ParserError
import pytest

app: AppConfig = AppConfig(map_path="path")


def test_non_existed_map() -> None:
    with pytest.raises(ParserError):
        parser = MapParser(app)
        parser.parse()


def test_empty_map() -> None:
    with pytest.raises(ParserError):
        parser = MapParser(app)
        parser.parse()
