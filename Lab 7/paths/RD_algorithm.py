from rdp import rdp
import csv
from pathlib import Path
import numpy as np

input_file = Path("data/global_pos_cleaned.csv")
output_file = Path("data/global_pos_RD_simplified.csv")

rows = np.loadtxt(input_file, delimiter=",")

timestamps = rows[:, 0]
latitudes = rows[:, 1]
longitudes = rows[:, 2]

points = np.column_stack((longitudes, latitudes))
simplified_points = rdp(points, epsilon=0.0001)

simplified_rows = rows[np.isin(points, simplified_points).all(axis=1)]


