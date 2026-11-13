import csv
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parent
INPUT_FILE = ROOT / "global_pos_27-29-10-13-11-2026.csv"
OUTPUT_FILE = ROOT / "global_pos_27-29-10-13-11-2026_utm.csv"
UTM_ZONE = 32
HEMISPHERE = "N"


def lat_lon_to_utm(latitude: float, longitude: float) -> tuple[float, float]:
    semi_major_axis = 6378137.0
    flattening = 1 / 298.257223563
    eccentricity_squared = flattening * (2 - flattening)
    second_eccentricity_squared = eccentricity_squared / (1 - eccentricity_squared)
    scale_factor = 0.9996
    central_meridian = math.radians((UTM_ZONE - 1) * 6 - 180 + 3)

    latitude_radians = math.radians(latitude)
    longitude_radians = math.radians(longitude)
    sin_latitude = math.sin(latitude_radians)
    cos_latitude = math.cos(latitude_radians)
    tangent_latitude = math.tan(latitude_radians)
    radius_of_curvature = semi_major_axis / math.sqrt(
        1 - eccentricity_squared * sin_latitude**2
    )
    meridian_distance = semi_major_axis * (
        (1 - eccentricity_squared / 4 - 3 * eccentricity_squared**2 / 64
         - 5 * eccentricity_squared**3 / 256) * latitude_radians
        - (3 * eccentricity_squared / 8 + 3 * eccentricity_squared**2 / 32
           + 45 * eccentricity_squared**3 / 1024) * math.sin(2 * latitude_radians)
        + (15 * eccentricity_squared**2 / 256
           + 45 * eccentricity_squared**3 / 1024) * math.sin(4 * latitude_radians)
        - (35 * eccentricity_squared**3 / 3072) * math.sin(6 * latitude_radians)
    )
    difference_longitude = longitude_radians - central_meridian
    a_term = cos_latitude * difference_longitude

    easting = scale_factor * radius_of_curvature * (
        a_term
        + (1 - tangent_latitude**2 + second_eccentricity_squared)
        * a_term**3 / 6
        + (5 - 18 * tangent_latitude**2 + tangent_latitude**4
           + 72 * second_eccentricity_squared
           - 58 * eccentricity_squared)
        * a_term**5 / 120
    ) + 500000
    northing = scale_factor * (
        meridian_distance
        + radius_of_curvature * tangent_latitude * (
            a_term**2 / 2
            + (5 - tangent_latitude**2 + 9 * second_eccentricity_squared
               + 4 * second_eccentricity_squared**2)
            * a_term**4 / 24
            + (61 - 58 * tangent_latitude**2 + tangent_latitude**4
               + 600 * second_eccentricity_squared
               - 330 * eccentricity_squared)
            * a_term**6 / 720
        )
    )
    return easting, northing


def main() -> None:
    with INPUT_FILE.open(newline="") as source, OUTPUT_FILE.open(
        "w", newline=""
    ) as destination:
        reader = csv.reader(source)
        writer = csv.writer(destination)
        writer.writerow(
            ["time_s", "easting_m", "northing_m", "heading_deg",
             "utm_zone", "hemisphere"]
        )
        for row in reader:
            time_s, latitude, longitude, heading_deg = map(float, row)
            easting, northing = lat_lon_to_utm(latitude, longitude)
            writer.writerow(
                [
                    f"{time_s:.9f}",
                    f"{easting:.3f}",
                    f"{northing:.3f}",
                    f"{heading_deg:.6f}",
                    UTM_ZONE,
                    HEMISPHERE,
                ]
            )
    print(f"Saved {OUTPUT_FILE} (UTM zone {UTM_ZONE}{HEMISPHERE})")


if __name__ == "__main__":
    main()
