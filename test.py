import subprocess
import os
from pathlib import Path
import math


INVALID_MAPS_DIR = Path("invalid_maps")


def run_no_rights_map(path: Path) -> None:
    original_mode = os.stat(path).st_mode
    try:
        os.chmod(path, 0)
        run_map(path)
    finally:
        os.chmod(path, original_mode)


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
    print(math.sqrt(25))


if __name__ == "__main__":
    main()
