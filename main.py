from src.simul.models import Hub, Connection
from src.parser import MapParser
from src.parser.models import ParsedHub
from src.cli import AppConfig
from dataclasses import asdict


def main():
    parsed = MapParser(AppConfig()).parse()
    hub1: ParsedHub = parsed[1]
    hub2 = parsed[2]
    connection1 = parsed[5]
    # hub1.connections.append(connection1)
    # hub2.connections.append(connection1)
    hub_dict = asdict(hub1)
    hub_meta_dict = asdict(hub1.meta)
    hub_full_dict = hub_dict | hub_meta_dict
    final = Hub(**hub_full_dict)
    print(final)


if __name__ == "__main__":
    main()
