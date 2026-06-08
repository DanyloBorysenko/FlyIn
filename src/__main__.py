import sys
from src.cli import AppConfigError, build_app_config
from src.parser import MapParser, ParserError
from src.simul import SimulationBuilder, SimulationError
from src.visualisation.visualizer import Visualizer
from src.simul import Solver


def main() -> None:
    try:
        app_config = build_app_config(sys.argv)
        if app_config.debug:
            print(f"AppConfig was created: {app_config}")
        parser = MapParser(app_config)
        parsed_maps = parser.parse_maps(app_config.playlist_path)
        simulations = SimulationBuilder(app_config).build_simul_map(
            parsed_maps)
        solver = Solver()
        solver.solve(simulations)
        if app_config.visual:
            Visualizer(app_config, simulations).run()
        else:
            solver.show_all_turns(simulations[0])
    except (AppConfigError, ParserError, SimulationError) as e:
        print(f"{e.__class__.__name__}: {e}", file=sys.stderr)
    except Exception as e:
        print(f"Unknown error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
