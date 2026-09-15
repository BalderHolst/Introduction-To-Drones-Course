#!/usr/bin/env python3

import sys
import numpy as np
import matplotlib.pyplot as plt

from nmea_read import *

input_path = sys.argv[1]

print ('Importing file')
nmea = nmea_class()
nmea.import_file(input_path)

data = []

for i, p in enumerate(nmea.data):
    label = p[0]
    if (label != '$GPGGA'): continue
    assert(len(p) == 15)

    [_, time, lat, _, lon, _, qual, sat, hdop, alt, alt_unit, georef, georef_unit, uu, _check] = p

    data.append([time, lat, lon, alt])

data = np.array(data).astype(np.float64)

t = data[:, 0]
x = data[:, 1]
y = data[:, 2]
z = data[:, 3]

fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(111, projection='3d')
# ax.plot(x, y, z, color='tab:red', linewidth=2)
ax.scatter(x, y, z, c=t, cmap='viridis', s=5)
# ax.colorbar(label='Time')
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')

plt.savefig(f"{input_path}.png")
