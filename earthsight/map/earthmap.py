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

        # set a custom map layout
        self.map.layout.height = '700px'

        # define imagery source
        self.s2 = Sentinel2()

        # build all widgets
        self.build_widgets()

        # throw on default visualization
        self.update_s2()
        self.visualize_s2()

    
    def update_s2(self):
        start_datetime = self.s2_date_start.value.strftime('%Y-%m-%d')
        end_datetime = self.s2_date_end.value.strftime('%Y-%m-%d')
        cloudy_pixel_pct = self.s2_cloudy_pixel.value
        cloud_mask = self.s2_cloud_mask.value
        temporal_op = self.s2_temporal_op.value

        self.s2.update(
            start_datetime,
            end_datetime,
            cloudy_pixel_pct,
            cloud_mask,
            temporal_op
        )


    def visualize_s2(self):
        band_parms = self._get_band_parms()
        url = self.s2.visualize(band_parms)
        self._add_layer(url, 'Sentinel-2')

    
    def build_widgets(self):
        self._build_s2_widgets()
        self._build_band_widgets()


    def show(self):
        return self.map


    def _add_layer(self, url, name):
        layer = ipyleaflet.TileLayer(url=url,
                                     name=name)
        self.map.add_layer(layer)


    def _get_band_parms(self):
        if self.single_band.value == True:
            band = self.gray_band_selector.value
            minval, maxval = self.gray_band_slider.value
            band_parms = ([band], [minval], [maxval])
        else:
            bands = [self.single_band_selectors[0].value,
                     self.single_band_selectors[1].value,
                     self.single_band_selectors[2].value]
            mins = [self.single_band_sliders[0].value[0],
                    self.single_band_sliders[1].value[0],
                    self.single_band_sliders[2].value[0]]
            maxs = [self.single_band_sliders[0].value[1],
                    self.single_band_sliders[1].value[1],
                    self.single_band_sliders[2].value[1]]
            band_parms = (bands, mins, maxs)

        return band_parms

    
    def _s2_button_click(self, event):
        if self.s2_button.button_style == 'info':
            self.s2_button.button_style = 'success'
            self.s2_parms.layout.display = 'block'
        else:
            self.s2_button.button_style = 'info'
            self.s2_parms.layout.display = 'none'


    def _band_button_click(self, event):
        if self.band_button.button_style == 'info':
            self.band_button.button_style = 'success'
            self.indiv_band_buttons.layout.display = 'block'
        else:
            self.band_button.button_style = 'info'
            self.indiv_band_buttons.layout.display = 'none'


    def _s2_observe(self, event):
        self.update_s2()
        self.visualize_s2()


    def _viz_observe(self, event):
        self.visualize_s2()
    

    def _band_presets_observe(self, event):
        preset = self.band_presets.value
        band_parms = self.s2.get_band_presets()[preset]

        bands, mins, maxs = band_parms

        for idx in range(len(bands)):
            band, minval, maxval = bands[idx], mins[idx], maxs[idx]
            if len(bands) == 1:
                self.single_band.value = True
                band_selector = self.gray_band_selector
                band_slider = self.gray_band_slider
            else:
                self.single_band.value = False
                band_selector = self.single_band_selectors[idx]
                band_slider = self.single_band_sliders[idx]

            band_selector.value = band
            band_slider.value = [minval, maxval]


    def _single_band_observe(self, event):
        if self.single_band.value == True:
            self.single_band_panes[0].layout.visibility = 'hidden'
            self.single_band_panes[1].layout.visibility = 'hidden'
            self.single_band_panes[2].layout.visibility = 'hidden'
            self.gray_band_pane.layout.visibility = 'visible'
        else:
            self.single_band_panes[0].layout.visibility = 'visible'
            self.single_band_panes[1].layout.visibility = 'visible'
            self.single_band_panes[2].layout.visibility = 'visible'
            self.gray_band_pane.layout.visibility = 'hidden'


    def _build_band_widgets(self):
        self.band_button = ipywidgets.Button(
            description='Visualize',
            disabled=False,
            button_style='info',
            tooltip='Configure visualization options'
        )
        self.band_button.on_click(self._band_button_click)

        band_preset_options = self.s2.get_band_presets().keys()
        self.band_presets = ipywidgets.Select(
            options=band_preset_options,
            value='True Color',
            description='See in',
            disabled=False
        )
        self.band_presets.observe(self._band_presets_observe)

        self.single_band = ipywidgets.Checkbox(
            value=False,
            description='Single band',
            disabled=False,
        )
        self.single_band.observe(self._single_band_observe)

        all_bands = self.s2.get_bands()
        all_band_options = [a[0] for a in all_bands]
        
        self.gray_band_selector = ipywidgets.Dropdown(
            options=all_band_options,
            value='probability',
            description='Gray',
            disabled=False
        )
        self.gray_band_selector.observe(self._viz_observe)

        self.gray_band_slider = ipywidgets.IntRangeSlider(
            value=[65, 100],
            min=0,
            max=100,
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d'
        )
        self.gray_band_slider.observe(self._viz_observe)

        self.gray_band_pane = ipywidgets.HBox(
            [self.gray_band_selector,
             self.gray_band_slider]
        )
        
        self.single_band_selectors = list()
        self.single_band_sliders = list()

        self.single_band_selectors.append(ipywidgets.Dropdown(
            options=all_band_options,
            value='B4',
            description='Red',
            disabled=False
        ))
        self.single_band_selectors[0].observe(self._viz_observe)

        self.single_band_sliders.append(ipywidgets.IntRangeSlider(
            value=[0, 3000],
            min=0,
            max=10000,
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d'
        ))
        self.single_band_sliders[0].observe(self._viz_observe)

        self.single_band_selectors.append(ipywidgets.Dropdown(
            options=all_band_options,
            value='B3',
            description='Green',
            disabled=False
        ))
        self.single_band_selectors[1].observe(self._viz_observe)

        self.single_band_sliders.append(ipywidgets.IntRangeSlider(
            value=[0, 3000],
            min=0,
            max=10000,
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d'
        ))
        self.single_band_sliders[1].observe(self._viz_observe)

        self.single_band_selectors.append(ipywidgets.Dropdown(
            options=all_band_options,
            value='B2',
            description='Blue',
            disabled=False
        ))
        self.single_band_selectors[2].observe(self._viz_observe)

        self.single_band_sliders.append(ipywidgets.IntRangeSlider(
            value=[0, 3000],
            min=0,
            max=10000,
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d'
        ))
        self.single_band_sliders[2].observe(self._viz_observe)

        self.single_band_panes = list()
        for band_selector, band_slider in zip(self.single_band_selectors, self.single_band_sliders):
            self.single_band_panes.append(
                ipywidgets.HBox(
                    [band_selector,
                     band_slider]
                )
            )

        self.histogram_button = ipywidgets.Button(
            description='Histogram',
            disabled=False,
            button_style='warning',
            tooltip='Compute histogram across bands over map region'
        )
        
        self.indiv_band_buttons = ipywidgets.VBox(
            [self.band_presets,
             self.single_band,
             self.gray_band_pane,
             self.single_band_panes[0],
             self.single_band_panes[1],
             self.single_band_panes[2],
             self.histogram_button]
        )
        
        self.indiv_band_buttons.layout.display = 'none'
        self.gray_band_pane.layout.visibility = 'hidden'

        band_button_control = ipyleaflet.WidgetControl(
            widget=self.band_button,
            position='topleft'
        )

        indiv_band_button_control = ipyleaflet.WidgetControl(
            widget=self.indiv_band_buttons,
            position='topleft'
        )
        
        self.map.add_control(band_button_control)
        self.map.add_control(indiv_band_button_control)


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

        # stack parameters in a VBox
        self.s2_parms = ipywidgets.VBox(
            [self.s2_date_start,
             self.s2_date_end,
             self.s2_cloudy_pixel,
             self.s2_cloud_mask,
             self.s2_temporal_op]
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

        
