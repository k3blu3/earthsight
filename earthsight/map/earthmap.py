'''
earthmap.py

EarthMap class definition that builds a custom ipyleaflet map
'''


import datetime
import ipyleaflet
import ipywidgets

from earthsight.imagery.sentinel2 import Sentinel2


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

        # build all widgets
        self.build_widgets()

        # define S2 imagery source
        self.s2 = Sentinel2()
        self.update_s2()

    
    def update_s2(self):
        start_datetime = self.s2_date_start.value.strftime('%Y-%m-%d')
        end_datetime = self.s2_date_end.value.strftime('%Y-%m-%d')
        cloudy_pixel_pct = self.s2_cloudy_pixel.value
        cloud_mask = self.s2_cloud_mask.value
        temporal_op = self.s2_temporal_op.value
        band_viz = self.s2_bands_viz.value

        self.s2.update(
            start_datetime,
            end_datetime,
            cloudy_pixel_pct,
            cloud_mask,
            temporal_op
        )

        url = self.s2.visualize(band_viz)
        self._add_layer(url, 'Sentinel-2')

    
    def build_widgets(self):
        self._build_s2_widgets()


    def show(self):
        return self.map


    def _add_layer(self, url, name):
        layer = ipyleaflet.TileLayer(url=url,
                                     name=name)
        self.map.add_layer(layer)


    def _s2_button_click(self, event):
        if self.s2_button.button_style == 'info':
            self.s2_button.button_style = 'success'
            self.s2_parms.layout.display = 'block'
        else:
            self.s2_button.button_style = 'info'
            self.s2_parms.layout.display = 'none'


    def _s2_observe(self, event):
        self.update_s2()


    def _build_s2_widgets(self):
        # build all widgets
        self.s2_button = ipywidgets.Button(
            description='Sentinel-2',
            disabled=False,
            button_style='info',
            tooltip='Configure imagery options',
        )
        self.s2_button.on_click(self._s2_button_click)

        self.s2_date_start = ipywidgets.DatePicker(
            description='Start',
            value=datetime.datetime(2020, 4, 1),
            disabled=False
        )
        self.s2_date_start.observe(self._s2_observe)

        self.s2_date_end = ipywidgets.DatePicker(
            description='End',
            value=datetime.datetime(2020, 8, 1),
            disabled=False
        ) 
        self.s2_date_end.observe(self._s2_observe)

        self.s2_cloudy_pixel = ipywidgets.IntSlider(
            value=100,
            min=0,
            max=100,
            step=1,
            description='Clouds',
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d'
        )
        self.s2_cloudy_pixel.observe(self._s2_observe)

        self.s2_cloud_mask = ipywidgets.Checkbox(
            value=False,
            description='Mask clouds',
            disabled=False,
        )
        self.s2_cloud_mask.observe(self._s2_observe)

        self.s2_temporal_op = ipywidgets.Dropdown(
            options=['mean', 'min', 'max', 'median', 'mosaic'],
            value='mean',
            description='Show',
            disabled=False
        )
        self.s2_temporal_op.observe(self._s2_observe)

        self.s2_bands_viz = ipywidgets.Dropdown(
            options=['True Color', 'Vegetation', 'Urban', 'Infrared'],
            value='True Color',
            description='How',
            disabled=False
        )
        self.s2_bands_viz.observe(self._s2_observe)
        
        # stack parameters in a VBox
        self.s2_parms = ipywidgets.VBox(
            [self.s2_date_start,
             self.s2_date_end,
             self.s2_cloudy_pixel,
             self.s2_cloud_mask,
             self.s2_temporal_op,
             self.s2_bands_viz]
        )

        # default don't show unless s2 button is presseed
        self.s2_parms.layout.display = 'none'
        
        # build widget controls for map
        s2_button_control = ipyleaflet.WidgetControl(
            widget=self.s2_button,
            position='topleft'
        )

        s2_parms_control = ipyleaflet.WidgetControl(
            widget=self.s2_parms,
            position='topleft'
        )

        self.map.add_control(s2_button_control)
        self.map.add_control(s2_parms_control)

        
