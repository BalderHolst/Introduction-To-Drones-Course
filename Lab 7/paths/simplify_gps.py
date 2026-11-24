import csv
from pathlib import Path
import numpy as np
from VW import VWSimplifier


input_file = Path("data/global_pos_cleaned.csv")
output_file = Path("data/global_pos_simplified.csv")

rows = np.loadtxt(input_file, delimiter=",")

timestamps = rows[:, 0]
latitudes = rows[:, 1]
longitudes = rows[:, 2]


points = np.column_stack((longitudes, latitudes))
simplifier = VWSimplifier(points)

threshold = np.quantile(simplifier.thresholds, 0.90)
keep = simplifier.thresholds >= threshold

simplified_rows = rows[keep]

np.savetxt(
    output_file,
    simplified_rows,
    delimiter=",",
    fmt="%.15g",
)

print(f"Original points:   {len(rows)}")
print(f"Simplified points: {len(simplified_rows)}")
print(f"Saved to:          {output_file}")