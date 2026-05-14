import sys
from src.cli import build_app_config
from src.cli import AppConfigError
# from src.cli.models import AppConfig


def main() -> None:
    try:
        app_config = build_app_config(sys.argv)
        print(app_config)
    except AppConfigError as e:
        print(f"{e.__class__.__name__}: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
