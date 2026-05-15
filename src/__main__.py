import sys
from src.cli import build_app_config
from src.cli import AppConfigError
from src.parser import MapParser


def main() -> None:
    try:
        app_config = build_app_config(sys.argv)
        if app_config.debug:
            print(f"AppConfig was created: {app_config}")
        parser = MapParser(app_config)
        parser.parse()
        MapParser(None).parse()
    except AppConfigError as e:
        print(f"{e.__class__.__name__}: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
