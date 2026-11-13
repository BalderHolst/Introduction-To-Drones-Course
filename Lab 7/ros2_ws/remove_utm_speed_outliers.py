import csv
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parent
INPUT_FILE = ROOT / "global_pos_27-29-10-13-11-2026_utm.csv"
OUTPUT_FILE = ROOT / "global_pos_27-29-10-13-11-2026_utm_cleaned.csv"
REPORT_FILE = ROOT / "global_pos_27-29-10-13-11-2026_speed_report.csv"
MAX_SPEED_KMH = 5.5


def segment_speed_kmh(previous: dict[str, str], current: dict[str, str]) -> float:
    delta_time_s = float(current["time_s"]) - float(previous["time_s"])
    if delta_time_s <= 0:
        raise ValueError(
            f"Non-positive time difference: {previous['time_s']} -> "
            f"{current['time_s']}"
        )
    distance_m = math.hypot(
        float(current["easting_m"]) - float(previous["easting_m"]),
        float(current["northing_m"]) - float(previous["northing_m"]),
    )
    return distance_m / delta_time_s * 3.6


def main() -> None:
    with INPUT_FILE.open(newline="") as source:
        rows = list(csv.DictReader(source))
    if not rows:
        raise ValueError(f"No data rows found in {INPUT_FILE}")

    fieldnames = list(rows[0])
    cleaned_rows = [rows[0]]
    last_kept_row_number = 1
    report_rows: list[dict[str, str]] = []
    for index, current in enumerate(rows[1:], start=2):
        previous = cleaned_rows[-1]
        speed_kmh = segment_speed_kmh(previous, current)
        is_outlier = speed_kmh > MAX_SPEED_KMH
        report_rows.append(
            {
                "segment_start_row": str(last_kept_row_number),
                "segment_end_row": str(index),
                "start_time_s": previous["time_s"],
                "end_time_s": current["time_s"],
                "speed_kmh": f"{speed_kmh:.6f}",
                "status": "removed" if is_outlier else "kept",
            }
        )
        if not is_outlier:
            cleaned_rows.append(current)
            last_kept_row_number = index

    with OUTPUT_FILE.open("w", newline="") as destination:
        writer = csv.DictWriter(destination, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(cleaned_rows)
    with REPORT_FILE.open("w", newline="") as destination:
        fieldnames = list(report_rows[0])
        writer = csv.DictWriter(destination, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(report_rows)

    removed_count = len(rows) - len(cleaned_rows)
    print(
        f"Saved {OUTPUT_FILE}: {len(cleaned_rows)} rows kept, "
        f"{removed_count} rows removed (threshold {MAX_SPEED_KMH:g} km/h)"
    )
    print(f"Saved {REPORT_FILE}: {len(report_rows)} segments")


if __name__ == "__main__":
    main()
