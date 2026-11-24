#!/usr/bin/env python3

import argparse
import csv
import json
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_INPUT = SCRIPT_DIR / "data" / "global_pos_cleaned.csv"
DEFAULT_OUTPUT = SCRIPT_DIR / "mission.plan"


def load_points(csv_path: Path) -> list[tuple[float, float, float]]:
    points = []

    with csv_path.open("r", newline="", encoding="utf-8") as csv_file:
        for line_number, row in enumerate(csv.reader(csv_file), start=1):
            if not row or all(not value.strip() for value in row):
                continue
            if len(row) < 3:
                raise ValueError(
                    f"{csv_path}: line {line_number} has fewer than three columns"
                )

            try:
                _, latitude, longitude, *altitude = row
                latitude = float(latitude)
                longitude = float(longitude)
                altitude_m = float(altitude[0]) if altitude else 30.0
            except ValueError as error:
                raise ValueError(
                    f"{csv_path}: invalid numeric value on line {line_number}"
                ) from error

            if not -90 <= latitude <= 90:
                raise ValueError(
                    f"{csv_path}: invalid latitude on line {line_number}: {latitude}"
                )
            if not -180 <= longitude <= 180:
                raise ValueError(
                    f"{csv_path}: invalid longitude on line {line_number}: {longitude}"
                )

            points.append((latitude, longitude, altitude_m))

    if not points:
        raise ValueError(f"{csv_path}: contains no waypoint rows")

    return points


def create_plan(
    points: list[tuple[float, float, float]],
    altitude_offset: float | None,
) -> dict:
    if altitude_offset is None:
        altitude_offset = points[0][2]

    items = []

    # Take off at the first recorded position.
    first_latitude, first_longitude, first_altitude = points[0]
    first_altitude_relative = max(0.0, first_altitude - altitude_offset)
    items.append({
        "autoContinue": True,
        "command": 22,
        "doJumpId": 1,
        "frame": 3,
        "params": [0, 0, 0, 0, first_latitude, first_longitude,
                   first_altitude_relative],
        "type": "SimpleItem",
    })

    # Add all remaining points as navigation waypoints.
    for jump_id, (latitude, longitude, altitude) in enumerate(
        points[1:], start=2
    ):
        altitude_relative = max(0.0, altitude - altitude_offset)
        items.append({
            "autoContinue": True,
            "command": 16,
            "doJumpId": jump_id,
            "frame": 3,
            "params": [0, 0, 0, 0, latitude, longitude,
                       altitude_relative],
            "type": "SimpleItem",
        })

    mission = {
        "cruiseSpeed": 5,
        "firmwareType": 3,
        "hoverSpeed": 2,
        "items": items,
        "plannedHomePosition": [
            first_latitude,
            first_longitude,
            first_altitude_relative,
        ],
        "vehicleType": 2,
        "version": 2,
    }

    return {
        "fileType": "Plan",
        "geoFence": {"polygon": [], "version": 1},
        "groundStation": "QGroundControl",
        "mission": mission,
        "rallyPoints": {"points": [], "version": 1},
        "version": 1,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert global_pos_cleaned.csv to a QGroundControl .plan file"
    )
    parser.add_argument("input", nargs="?", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("-o", "--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--altitude-offset",
        type=float,
        default=None,
        help="Subtract this value from CSV altitudes "
             "(defaults to the first CSV altitude)",
    )
    args = parser.parse_args()

    input_path = args.input.resolve()
    output_path = args.output.resolve()
    points = load_points(input_path)
    plan = create_plan(points, args.altitude_offset)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(plan, indent=4, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(f"Saved {output_path} ({len(points)} GPS points)")


if __name__ == "__main__":
    main()
