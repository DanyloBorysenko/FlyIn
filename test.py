import subprocess
from pathlib import Path


INVALID_MAPS_DIR = Path("invalid_maps")


def run_map(map_path: Path) -> None:
    cmd = (
        f'make run '
        f'ARGS="--map-path={map_path}"'
    )

    print(f"\n{'=' * 60}")
    print(f"RUNNING: {map_path}")
    print(f"{'=' * 60}\n")

    subprocess.run(
        cmd,
        shell=True,
    )


def main() -> None:
    maps = sorted(INVALID_MAPS_DIR.rglob("*.txt"))

    for map_path in maps:
        run_map(map_path)


if __name__ == "__main__":
    main()
