'''
earthmap.py

EarthMap class definition that builds a custom ipyleaflet map
'''


import bqplot as bq
import datetime
import ipyleaflet as ipyl


from earthsight.map.basemaps import BASEMAPS
from earthsight.map.histogram import Histogram
from earthsight.map.imagery import Imagery
from earthsight.map.layers import Layers
from earthsight.map.visualize import Visualize
from earthsight.utils.constants import (BASEMAP_DEFAULT,
                                        CENTER_DEFAULT,
                                        ZOOM_DEFAULT)


class EarthMap:
    def __init__(self,
                 basemap=BASEMAP_DEFAULT,
                 center=CENTER_DEFAULT,
                 zoom=ZOOM_DEFAULT):
        # create leaflet map
        self.map = self.create_map(basemap, center, zoom)

        # add basic interactive controls
        self.add_base_controls()

        # control layers 
        self.layers = Layers(self.map)

        # control imagery options
        self.imagery = Imagery(self.map, self.layers)

        # control visualize options
        self.visualize = Visualize(self.map, self.layers)

        # control histogram options
        self.histogram = Histogram(self.map, self.layers)


    def create_map(self, basemap, center, zoom):
        # define map kwargs
        map_kwargs = dict()
        map_kwargs['center'] = center
        map_kwargs['zoom'] = zoom
        map_kwargs['zoom_control'] = False
        map_kwargs['attribution_control'] = False
        map_kwargs['scroll_wheel_zoom'] = True

        # build map
        m = ipyl.Map(basemap=basemap, **map_kwargs)
        
        # set layout height
        m.layout.height = '700px'
        
        return m

    
    def add_base_controls(self):
        zc = ipyl.ZoomControl(position='topright')
        self.map.add_control(zc)

        sc = ipyl.ScaleControl(position='bottomleft')
        self.map.add_control(sc)

        fsc = ipyl.FullScreenControl(position='topright')
        self.map.add_control(fsc)

        dc = ipyl.DrawControl(position='topright')
        dc.marker = {}
        dc.rectangle = {}
        dc.circle = {}
        dc.polyline = {}
        dc.circlemarker = {}
        dc.polygon = {
            'shapeOptions': {
                'color': '#81d8d0',
                'fill_color': '#81d8d0',
                'weight': 4,
                'opacity': 1.0,
                'fill_opacity': 0.7
            }
        }
        self.map.add_control(dc)


    def show(self):
        return self.map


