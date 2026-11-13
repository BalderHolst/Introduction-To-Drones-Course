import csv
from pathlib import Path
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parent
INPUT_FILE = ROOT / "global_pos_27-29-10-13-11-2026.csv"
OUTPUT_FILE = ROOT / "global_pos_27-29-10-13-11-2026_qgc.kml"
KML_NAMESPACE = "http://www.opengis.net/kml/2.2"


def load_rows() -> list[tuple[float, float, float, float]]:
    with INPUT_FILE.open(newline="") as csv_file:
        return [
            tuple(float(value) for value in row)
            for row in csv.reader(csv_file)
        ]


def main() -> None:
    rows = load_rows()
    ET.register_namespace("", KML_NAMESPACE)
    kml = ET.Element(f"{{{KML_NAMESPACE}}}kml")
    document = ET.SubElement(kml, f"{{{KML_NAMESPACE}}}Document")
    ET.SubElement(document, f"{{{KML_NAMESPACE}}}name").text = (
        "Global position track"
    )

    track = ET.SubElement(document, f"{{{KML_NAMESPACE}}}Placemark")
    ET.SubElement(track, f"{{{KML_NAMESPACE}}}name").text = "Track"
    line_string = ET.SubElement(track, f"{{{KML_NAMESPACE}}}LineString")
    ET.SubElement(line_string, f"{{{KML_NAMESPACE}}}tessellate").text = "1"
    ET.SubElement(line_string, f"{{{KML_NAMESPACE}}}altitudeMode").text = (
        "clampToGround"
    )
    coordinates = ET.SubElement(line_string, f"{{{KML_NAMESPACE}}}coordinates")
    coordinates.text = " ".join(
        f"{longitude:.8f},{latitude:.8f},0"
        for _, latitude, longitude, _ in rows
    )

    ET.indent(kml, space="  ")
    ET.ElementTree(kml).write(
        OUTPUT_FILE,
        encoding="utf-8",
        xml_declaration=True,
    )
    print(f"Saved {OUTPUT_FILE} ({len(rows)} points)")


if __name__ == "__main__":
    main()
