'''
gee.py

Python utilities for working with Google Earth Engine
'''


import ee


def image_to_tiles(image, vis_params=None):
    map_id = image.getMapId(vis_params)
    return map_id['tile_fetcher'].url_format



