import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

from great_circle import great_circle
import VW

class PathSimplifier:
    def __init__(self, input_path) -> None:

        rows = np.loadtxt(input_path, delimiter=",")

        lats = rows[:, 1]
        lons = rows[:, 2]

        points = len(lats)

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

    def visvalingam_whyatt(self, max_dist: float):
        points = np.column_stack((self.lon, self.lat))
        simplifier = VW.VWSimplifier(points)

        threshold = np.quantile(simplifier.thresholds, max_dist)
        keep = simplifier.thresholds >= threshold

        simplified_rows = points[keep]

        lat = points[:, 1]
        lon = points[:, 0]

        return (lat, lon)




if __name__ == "__main__":
    p = PathSimplifier("./data/global_pos_cleaned.csv")
    print(np.sum(p.distances))
    plt.plot(*p.latlon(), label="Original")
    # plt.plot(*p.simple_smooth(20), label="Simple Smooth")
    plt.plot(*p.visvalingam_whyatt(0.5), label="Visvalingam-Whyatt")
    plt.legend()
    plt.show()
