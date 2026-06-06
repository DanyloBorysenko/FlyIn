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
        parsed_elements = parser.parse_map(app_config.map_path)
        parsed_maps = parser.parse_maps(app_config.playlist_path)
        for name, els in parsed_maps.items():
            print(f"\nName: {name}, els: {els}")
        simul = SimulationBuilder(app_config, parsed_maps).build_simulation(parsed_elements)
        if app_config.debug:
            print(f"\nSimulationMap was built: {simul}")
        solver = Solver(simul)
        solver.solve()
        if app_config.visual:
            Visualizer(app_config, simul, solver).run()
        else:
            solver.show_all_turns()
    except (AppConfigError, ParserError, SimulationError) as e:
        print(f"{e.__class__.__name__}: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
