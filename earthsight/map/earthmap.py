'''
earthmap.py

EarthMap class definition that builds a custom ipyleaflet map
'''


import ipyleaflet


BASEMAP_DEFAULT = ipyleaflet.basemaps.OpenStreetMap.HOT
CENTER_DEFAULT = (35.7004, -105.9136)
ZOOM_DEFAULT = 9

class EarthMap:
    def __init__(self,
                 basemap=BASEMAP_DEFAULT,
                 center=CENTER_DEFAULT,
                 zoom=ZOOM_DEFAULT):
        # define map kwargs
        map_kwargs = dict()
        map_kwargs['center'] = center
        map_kwargs['zoom'] = zoom
        map_kwargs['zoom_control'] = False
        map_kwargs['attribution_control'] = False
        map_kwargs['scroll_wheel_zoom'] = True

        # build map
        self.map = ipyleaflet.Map(basemap=basemap,
                                  **map_kwargs)

        # add useful controls
        zc = ipyleaflet.ZoomControl(position='topright')
        self.map.add_control(zc)

        sc = ipyleaflet.ScaleControl(position='bottomleft')
        self.map.add_control(sc)

        fsc = ipyleaflet.FullScreenControl(position='topright')
        self.map.add_control(fsc)

        dc = ipyleaflet.DrawControl(position='topright')
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

        # set a better layout
        self.map.layout.width = '960px'
        self.map.layout.height = '540px'


    def show(self):
        return self.map


    def add_layer(self, url, name):
        layer = ipyleaflet.TileLayer(url=url,
                                     name=name)
        self.map.add_layer(layer)




        



        
