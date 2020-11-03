'''
earthmap.py

EarthMap class definition that builds a custom ipyleaflet map
'''


import bqplot as bq
import datetime
import ipyleaflet as ipyl


from earthsight.map.earthwidgets import EarthWidgets
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
        
        # add custom widgets
        self.widgets = EarthWidgets(self.map)
        self.add_custom_widgets()


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


    def add_custom_widgets(self):
        # add img button and corresponding pane to the map
        self.widgets.build_img_button()
        self.widgets.build_img_pane()

        self.map.add_control(
            ipyl.WidgetControl(
                widget=self.widgets.img_button,
                position='topleft'
            )
        )

        self.map.add_control(
            ipyl.WidgetControl(
                widget=self.widgets.img_pane,
                position='topleft'
            )
        )

        # add viz button and corresponding pane to the map
        self.widgets.build_viz_button()
        self.widgets.build_viz_pane()

        self.map.add_control(
            ipyl.WidgetControl(
                widget=self.widgets.viz_button,
                position='topleft'
            )
        )

        self.map.add_control(
            ipyl.WidgetControl(
                widget=self.widgets.viz_pane,
                position='topleft'
            )
        )

        # add histogram button and correpsonding pane to the map
        self.widgets.build_hist_button()

        self.map.add_control(
            ipyl.WidgetControl(
                widget=self.widgets.hist_button,
                position='topleft'
            )
        )


    def show(self):
        return self.map


