import csv

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


input_file = "ros2_ws/global_pos_27-29-10-13-11-2026_rdp.csv"
output_file = "ros2_ws/flight_path.png"


with open(input_file, newline="") as file:
    rows = list(csv.reader(file))

latitudes = [float(row[1]) for row in rows]
longitudes = [float(row[2]) for row in rows]

plt.plot(longitudes, latitudes)
plt.scatter(longitudes[0], latitudes[0], label="start")
plt.scatter(longitudes[-1], latitudes[-1], label="end")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.title("Flight path")
plt.legend()
plt.axis("equal")
plt.savefig(output_file)
print(f"Saved {output_file}")
