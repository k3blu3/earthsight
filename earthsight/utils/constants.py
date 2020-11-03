'''
constants.py

Constant parameters useful across codebase
'''


import ipyleaflet as ipyl


BASEMAP_DEFAULT = ipyl.basemaps.OpenStreetMap.HOT # OSM basemap is easy to navigate
CENTER_DEFAULT = (35.7004, -105.9136) # Center of map default in Santa Fe
ZOOM_DEFAULT = 9 # Default zoom level


# governs the scale as a function of zoom level for histogram computation
ZOOM_TO_SCALE = {
    0: 156412,
    1: 78206,
    2: 39103,
    3: 19551,
    4: 9776,
    5: 4888,
    6: 2444,
    7: 1222,
    8: 611,
    9: 305,
    10: 152,
    11: 76,
    12: 38,
    13: 19,
    14: 10,
    15: 5,
    16: 3,
    17: 2,
    18: 1,
    19: 0.5,
    20: 0.1
}
