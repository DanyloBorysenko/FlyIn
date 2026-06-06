from src.parser import MapParser
from src.cli import AppConfig


def main():
    parsed = MapParser(AppConfig()).parse_map()
    print(parsed)


if __name__ == "__main__":
    main()
