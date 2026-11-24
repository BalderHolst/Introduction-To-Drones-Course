import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

from great_circle import great_circle

class PathSimplifier:
    def __init__(self, input_path) -> None:

        csv_lines = Path(input_path).read_text().splitlines()

        points = len(csv_lines)

        lats = np.zeros(points)
        lons = np.zeros(points)

        for i, line in enumerate(csv_lines):
            [_, lat, lon, _] = line.strip().split(',')
            lats[i] = float(lat)
            lons[i] = float(lon)

        self.lat = lats
        self.lon = lons
        self.points = points

        self.distances = np.zeros(points-1)
        for i in range(1, self.points):
            lat1 = self.lat[i-1]
            lon1 = self.lon[i-1]
            lat2 = self.lat[i]
            lon2 = self.lon[i]
            self.distances[i-1] = great_circle(lat1, lon1, lat2, lon2)


    def latlon(self):
        return (self.lat, self.lon)

    def simple_smooth(self, points: int):
        spacing = np.sum(self.distances) / (points - 1)

        # Cumulative distance along the line
        cumulative = np.insert(np.cumsum(self.distances), 0, 0)

        # New equally spaced positions
        s = np.arange(0, cumulative[-1], spacing)

        # Interpolate x and y independently
        lat = np.interp(s, cumulative, self.lat)
        lon = np.interp(s, cumulative, self.lon)

        return (lat, lon)




if __name__ == "__main__":
    p = PathSimplifier("./data/global_pos_cleaned.csv")
    print(np.sum(p.distances))
    plt.plot(*p.latlon())
    plt.plot(*p.simple_smooth(20))
    plt.show()
