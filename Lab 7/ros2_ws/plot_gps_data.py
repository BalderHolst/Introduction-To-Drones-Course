from pathlib import Path
import csv

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parent
GLOBAL_FILE = ROOT / "global_pos_27-29-10-13-11-2026.csv"
GPS1_FILE = ROOT / "gps1_raw_27-29-10-13-11-2026.csv"
RAW_FIX_FILE = ROOT / "raw_fix_27-29-10-13-11-2026.csv"
OUTPUT_FILE = ROOT / "gps_latitude_vs_longitude.png"


def load_data() -> tuple[dict[str, list[float]], ...]:
    def read_rows(path: Path, columns: tuple[str, ...]) -> dict[str, list[float]]:
        data = {column: [] for column in columns}
        with path.open(newline="") as csv_file:
            for row in csv.reader(csv_file):
                for column, value in zip(columns, row, strict=True):
                    data[column].append(float(value))
        return data

    global_pos = read_rows(
        GLOBAL_FILE, ("time_s", "latitude", "longitude", "heading_deg")
    )
    gps1_raw = read_rows(
        GPS1_FILE, ("time_s", "status", "latitude", "longitude", "altitude_m")
    )
    raw_fix = read_rows(
        RAW_FIX_FILE, ("time_s", "status", "latitude", "longitude", "altitude_m")
    )
    return global_pos, gps1_raw, raw_fix


def main() -> None:
    global_pos, gps1_raw, raw_fix = load_data()

    datasets = (
        ("Global position", global_pos, "tab:blue"),
        ("GPS1 raw", gps1_raw, "tab:orange"),
        ("Raw fix", raw_fix, "tab:green"),
    )
    fig, axes = plt.subplots(1, 3, figsize=(18, 6), constrained_layout=True)

    for axis, (title, data, color) in zip(axes, datasets, strict=True):
        axis.plot(
            data["longitude"],
            data["latitude"],
            color=color,
            linewidth=1.5,
        )
        axis.scatter(
            data["longitude"][0],
            data["latitude"][0],
            color="black",
            marker="o",
            zorder=5,
            label="Start",
        )
        axis.scatter(
            data["longitude"][-1],
            data["latitude"][-1],
            color="black",
            marker="x",
            s=70,
            zorder=5,
            label="End",
        )
        axis.set_title(title)
        axis.set_xlabel("Longitude (deg)")
        axis.set_ylabel("Latitude (deg)")
        axis.grid(True, alpha=0.3)
        axis.legend()
        axis.set_aspect("equal", adjustable="datalim")

    fig.suptitle("Latitude vs longitude")
    fig.savefig(OUTPUT_FILE, dpi=180)
    print(f"Saved {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
