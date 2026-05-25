from src.simul.models import Hub, Connection
from src.parser import MapParser
from src.cli import AppConfig


def main():
    parsed = MapParser(AppConfig()).parse()
    hub1 = parsed[1]
    hub2 = parsed[2]
    connection1 = parsed[5]
    # hub1.connections.append(connection1)
    # hub2.connections.append(connection1)
    print(hub1)
    print(hub2)
    print(connection1)


if __name__ == "__main__":
    main()
