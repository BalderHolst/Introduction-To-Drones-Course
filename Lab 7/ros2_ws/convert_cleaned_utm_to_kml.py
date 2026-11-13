import csv
import math
from pathlib import Path
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parent
INPUT_FILE = ROOT / "global_pos_27-29-10-13-11-2026_utm_cleaned.csv"
OUTPUT_FILE = ROOT / "global_pos_27-29-10-13-11-2026_utm_cleaned.kml"
KML_NAMESPACE = "http://www.opengis.net/kml/2.2"


def utm_to_lat_lon(
    easting: float, northing: float, zone: int, hemisphere: str
) -> tuple[float, float]:
    semi_major_axis = 6378137.0
    flattening = 1 / 298.257223563
    eccentricity_squared = flattening * (2 - flattening)
    scale_factor = 0.9996
    central_meridian = math.radians((zone - 1) * 6 - 180 + 3)

    x = easting - 500000
    y = northing if hemisphere.upper() == "N" else northing - 10000000
    meridian_distance = y / scale_factor
    footpoint_latitude = meridian_distance / (
        semi_major_axis
        * (1 - eccentricity_squared / 4
           - 3 * eccentricity_squared**2 / 64
           - 5 * eccentricity_squared**3 / 256)
    )
    e1 = (1 - math.sqrt(1 - eccentricity_squared)) / (
        1 + math.sqrt(1 - eccentricity_squared)
    )
    eccentricity_prime_squared = eccentricity_squared / (1 - eccentricity_squared)
    footpoint_latitude += (
        (3 * e1 / 2 - 27 * e1**3 / 32)
        * math.sin(2 * footpoint_latitude)
        + (21 * e1**2 / 16 - 55 * e1**4 / 32)
        * math.sin(4 * footpoint_latitude)
        + (151 * e1**3 / 96) * math.sin(6 * footpoint_latitude)
        + (1097 * e1**4 / 512) * math.sin(8 * footpoint_latitude)
    )
    sin_footpoint = math.sin(footpoint_latitude)
    cos_footpoint = math.cos(footpoint_latitude)
    tangent_footpoint = math.tan(footpoint_latitude)
    radius_of_curvature = semi_major_axis / math.sqrt(
        1 - eccentricity_squared * sin_footpoint**2
    )
    radius_meridian = (
        semi_major_axis * (1 - eccentricity_squared)
        / (1 - eccentricity_squared * sin_footpoint**2) ** 1.5
    )
    latitude = footpoint_latitude - (
        radius_of_curvature * tangent_footpoint / radius_meridian
    ) * (
        x**2 / (2 * scale_factor**2 * radius_of_curvature**2)
        - (5 + 3 * tangent_footpoint**2
           + 10 * eccentricity_prime_squared * cos_footpoint**2
           - 4 * eccentricity_prime_squared**2 * cos_footpoint**4
           - 9 * eccentricity_prime_squared)
        * x**4 / (24 * scale_factor**4 * radius_of_curvature**4)
    )
    longitude = central_meridian + (
        x / (scale_factor * radius_of_curvature * cos_footpoint)
        - (1 + 2 * tangent_footpoint**2 + eccentricity_prime_squared
           * cos_footpoint**2)
        * x**3 / (6 * scale_factor**3 * radius_of_curvature**3
                  * cos_footpoint)
    )
    return math.degrees(latitude), math.degrees(longitude)


def main() -> None:
    with INPUT_FILE.open(newline="") as csv_file:
        rows = list(csv.DictReader(csv_file))
    if not rows:
        raise ValueError(f"No data rows found in {INPUT_FILE}")

    ET.register_namespace("", KML_NAMESPACE)
    kml = ET.Element(f"{{{KML_NAMESPACE}}}kml")
    document = ET.SubElement(kml, f"{{{KML_NAMESPACE}}}Document")
    ET.SubElement(document, f"{{{KML_NAMESPACE}}}name").text = (
        "Cleaned global position track"
    )
    track = ET.SubElement(document, f"{{{KML_NAMESPACE}}}Placemark")
    ET.SubElement(track, f"{{{KML_NAMESPACE}}}name").text = "Track"
    line_string = ET.SubElement(track, f"{{{KML_NAMESPACE}}}LineString")
    ET.SubElement(line_string, f"{{{KML_NAMESPACE}}}tessellate").text = "1"
    ET.SubElement(line_string, f"{{{KML_NAMESPACE}}}altitudeMode").text = (
        "clampToGround"
    )
    coordinates = ET.SubElement(line_string, f"{{{KML_NAMESPACE}}}coordinates")
    coordinate_values = []
    for row in rows:
        latitude, longitude = utm_to_lat_lon(
            float(row["easting_m"]),
            float(row["northing_m"]),
            int(row["utm_zone"]),
            row["hemisphere"],
        )
        coordinate_values.append(f"{longitude:.8f},{latitude:.8f},0")
    coordinates.text = " ".join(coordinate_values)

    ET.indent(kml, space="  ")
    ET.ElementTree(kml).write(
        OUTPUT_FILE,
        encoding="utf-8",
        xml_declaration=True,
    )
    print(f"Saved {OUTPUT_FILE} ({len(rows)} points)")


if __name__ == "__main__":
    main()
