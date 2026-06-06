import pytest
from src.cli import AppConfigError
from src.cli import build_app_config


def test_unknown_flag() -> None:
    with pytest.raises(AppConfigError):
        build_app_config(["filename", "--map"])


def test_default_args() -> None:
    app = build_app_config(["filename"])
    assert app.map_path == "maps/easy/01_linear_path.txt"
    assert app.playlist_path == "maps"
    assert app.debug is False


def test_map_flag() -> None:
    app = build_app_config(["filename", "--map-path=new"])
    assert app.map_path == "new"


def test_playlist_flag() -> None:
    app = build_app_config(["filename", "--playlist-path=new"])
    assert app.playlist_path == "new"


def test_debug_flag() -> None:
    app = build_app_config(["filename", "--debug"])
    assert app.debug is True


def test_debug_flag_with_val() -> None:
    with pytest.raises(AppConfigError):
        build_app_config(["filename", "--debug=False"])
