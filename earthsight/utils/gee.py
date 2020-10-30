'''
gee.py

Python utilities for working with Google Earth Engine
'''


import ee
from shapely.geometry import box, mapping


def image_to_tiles(image, vis_params=None):
    map_id = image.getMapId(vis_params)
    return map_id['tile_fetcher'].url_format


def bounds_to_geom(bounds):
    '''
    take bounds from a leaflet map and convert to ee.Geometry
    '''

    # create shapely polygon from bounds
    min_lat, min_lon = bounds[0]
    max_lat, max_lon = bounds[1]

    geojson_poly = mapping(box(min_lon, min_lat, max_lon, max_lat))
    
    geom = ee.Geometry(geojson_poly)
    return geom





