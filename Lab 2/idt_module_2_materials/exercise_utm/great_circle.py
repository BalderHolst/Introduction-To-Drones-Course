from math import *

R = 6_371_000

def deg_to_rad(deg):
    return deg * pi / 180

def great_circle_bad(lat1, lon1, lat2, lon2):
    return acos(sin(lat1) * sin(lat2) + cos(lat1) * cos(lat2) * cos(lon1 - lon2))

def great_circle(lat1, lon1, lat2, lon2):
    lat1 = deg_to_rad(lat1)
    lat2 = deg_to_rad(lat2)
    lon1 = deg_to_rad(lon1)
    lon2 = deg_to_rad(lon2)
    return R * (
            2 * asin(sqrt(
                (sin((lat1-lat2)/2))**2 + cos(lat1) * cos(lat2)
                * (sin((lon1-lon2)/2))**2))
    )
