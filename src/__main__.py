import sys
from src.cli import AppConfigError, build_app_config
from src.parser import MapParser, ParserError
from src.simul import SimulationBuilder


def main() -> None:
    try:
        app_config = build_app_config(sys.argv)
        if app_config.debug:
            print(f"AppConfig was created: {app_config}")
        parsed_elements = MapParser(app_config).parse()
        map = SimulationBuilder(app_config).build_sim_map(parsed_elements)
        if app_config.debug:
            print(f"\nSimulationMap was built: {map}")
    except (AppConfigError, ParserError) as e:
        print(f"{e.__class__.__name__}: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
