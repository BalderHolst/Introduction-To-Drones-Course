from pathlib import Path
import json

path = Path("paths/data/global_pos_cleaned.csv")

coordinates = []

for line in path.read_text().splitlines():
    [_, lat, lon, _] = line.strip().split(',')
    coordinates.append([lat, lon])

data = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {},
            "geometry": {
                "type": "LineString",
                "coordinates": coordinates
            }
        }
    ]
}
out_path = path.with_suffix('.json')

print(out_path)
with open(out_path, 'w') as f:
    json.dump(data, f, indent=4)