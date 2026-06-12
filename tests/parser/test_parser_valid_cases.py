from src.cli import AppConfig
from src.parser import MapParser
from src.domain import ZoneType, HubKind
from src.parser.models import (ParsedNbDrones, ParsedHub, ParsedConnection,
                               HubMetadata, ConnectionMetadata)


def test_default_metadata() -> None:
    app = AppConfig(map_path="tests/parser/valid_maps/default_metadata.txt")
    actual = MapParser(app).parse_map(
        "tests/parser/valid_maps/default_metadata.txt")
    expected = [
        ParsedNbDrones(line_ind=1, drones_count=2),
        ParsedHub(
            line_ind=3,
            kind=HubKind.START,
            name="start",
            coord_x=0,
            coord_y=0,
            meta=HubMetadata(
                line_ind=3, zone=ZoneType.NORMAL,
                color=None, max_drones=1)),

        ParsedHub(
            line_ind=4,
            kind=HubKind.STANDARD,
            name="waypoint1",
            coord_x=1,
            coord_y=0,
            meta=HubMetadata(
                line_ind=4, zone=ZoneType.NORMAL,
                color=None, max_drones=1)),

        ParsedHub(
            line_ind=5,
            kind=HubKind.END,
            name="goal",
            coord_x=3,
            coord_y=0,
            meta=HubMetadata(
                line_ind=5, zone=ZoneType.NORMAL,
                color=None, max_drones=1)),

        ParsedConnection(
            line_ind=7,
            zone1="start",
            zone2="waypoint1",
            meta=ConnectionMetadata(max_link_capacity=1, line_ind=7)),

        ParsedConnection(
            line_ind=8,
            zone1="waypoint1",
            zone2="goal",
            meta=ConnectionMetadata(max_link_capacity=1, line_ind=8))
                ]
    assert expected == actual


def test_full_metadata() -> None:
    app = AppConfig(
        map_path="tests/parser/valid_maps/full_metadata.txt"
    )

    actual = MapParser(app).parse_map(
        "tests/parser/valid_maps/full_metadata.txt")

    expected = [
        ParsedNbDrones(
            line_ind=1,
            drones_count=12,
        ),

        ParsedHub(
            line_ind=3,
            kind=HubKind.START,
            name="start",
            coord_x=0,
            coord_y=0,
            meta=HubMetadata(
                line_ind=3,
                zone=ZoneType.NORMAL,
                color="green",
                max_drones=12,
            ),
        ),

        ParsedHub(
            line_ind=4,
            kind=HubKind.STANDARD,
            name="restricted_tunnel1",
            coord_x=4,
            coord_y=0,
            meta=HubMetadata(
                line_ind=4,
                zone=ZoneType.RESTRICTED,
                color="red",
                max_drones=2,
            ),
        ),

        ParsedHub(
            line_ind=5,
            kind=HubKind.STANDARD,
            name="priority_bypass1",
            coord_x=4,
            coord_y=1,
            meta=HubMetadata(
                line_ind=5,
                zone=ZoneType.PRIORITY,
                color="cyan",
                max_drones=3,
            ),
        ),

        ParsedHub(
            line_ind=6,
            kind=HubKind.STANDARD,
            name="gate1_blocked",
            coord_x=1,
            coord_y=0,
            meta=HubMetadata(
                line_ind=6,
                zone=ZoneType.BLOCKED,
                color="orange",
            ),
        ),

        ParsedHub(
            line_ind=7,
            kind=HubKind.END,
            name="goal",
            coord_x=9,
            coord_y=0,
            meta=HubMetadata(
                line_ind=7,
                color="green",
                max_drones=12,
            ),
        ),

        ParsedConnection(
            line_ind=9,
            zone1="start",
            zone2="restricted_tunnel1",
            meta=ConnectionMetadata(
                line_ind=9,
                max_link_capacity=1,
            ),
        ),

        ParsedConnection(
            line_ind=10,
            zone1="priority_bypass1",
            zone2="goal",
            meta=ConnectionMetadata(
                line_ind=10,
                max_link_capacity=1
            )
        ),
    ]

    assert expected == actual


def test_line_with_spaces_only() -> None:
    app = AppConfig(
        map_path="tests/parser/valid_maps/line_with_spaces_only.txt")
    MapParser(app=app).parse_map(
        "tests/parser/valid_maps/line_with_spaces_only.txt")
