from src.parser import ParsedConnection
from src.parser.models import ConnectionMetadata


def main():
    meta = ConnectionMetadata(line_ind=1)
    conn1 = ParsedConnection(line_ind=1, zone1="start", zone2="hub1", meta=meta)
    conn2 = ParsedConnection(line_ind=1, zone1="hub1", zone2="start", meta=meta)
    print(conn1 == conn2)


if __name__ == "__main__":
    main()
