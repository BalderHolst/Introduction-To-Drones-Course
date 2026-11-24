from pathlib import Path

import numpy as np
import matplotlib

from great_circle import great_circle

matplotlib.use("Agg")
import matplotlib.pyplot as plt

INPUT_FILE = Path(__file__).parent / "data" / "global_pos.csv"
OUTPUT_FILE = Path(__file__).parent / "data" / "global_pos_cleaned.csv"

data = np.loadtxt(INPUT_FILE, delimiter=",", skiprows=0)

t   = data[:, 0]
lat = data[:, 1]
lon = data[:, 2]


## Plot raw data

plt.figure(figsize=(10, 8))
plt.scatter(lon, lat)

plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.title("GPS Path")
plt.axis("equal")
plt.grid(True)

output_file = Path(__file__).with_name("gps_path.png")
plt.savefig(output_file, dpi=150, bbox_inches="tight")
print(f"Plot saved to {output_file}")



## Remove points
THRESHOLD = 5 / 3.6 # m / s

valid_indices = []
current_index = 0
while current_index + 1 < len(t):
    time_diff = t[current_index + 1] - t[current_index]
    distance = great_circle(
        lat[current_index], lon[current_index],
        lat[current_index + 1], lon[current_index + 1],
    )

    if time_diff > 0 and distance / time_diff < THRESHOLD:
        break

    current_index += 1
else:
    raise ValueError("No consecutive GPS points meet the walking-speed threshold")

while current_index < len(t):
    valid_indices.append(current_index)
    next_index = current_index + 1

    while next_index < len(t):
        distance = great_circle(lat[current_index], lon[current_index], lat[next_index], lon[next_index])
        time_diff = t[next_index] - t[current_index]
        speed = distance / time_diff

        if speed < THRESHOLD: break

        next_index += 1

    current_index = next_index

t   = t[valid_indices]
lat = lat[valid_indices]
lon = lon[valid_indices]

plt.figure(figsize=(10, 8))
plt.plot(lon, lat)

# Plot clean GPS path
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.title("Clean GPS Path")
plt.axis("equal")
plt.grid(True)

# Plot start end and points
plt.scatter(lon[0], lat[0], color="green", label="Start", zorder=5)
plt.scatter(lon[-1], lat[-1], color="red", label="End", zorder=5)
plt.legend()

output_file = Path(__file__).with_name("gps_path_clean.png")
plt.savefig(output_file, dpi=150, bbox_inches="tight")
print(f"Plot saved to {output_file}")


cleaned_data = data[valid_indices]
np.savetxt(OUTPUT_FILE, cleaned_data, delimiter=",", fmt="%.18g")
print(f"Cleaned data saved to {OUTPUT_FILE}")
