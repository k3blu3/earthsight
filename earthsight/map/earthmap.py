'''
earthmap.py

EarthMap class definition that builds a custom ipyleaflet map
'''


import bqplot as bq
import datetime
import ipyleaflet
import ipywidgets

from earthsight.imagery.sentinel2 import Sentinel2


BASEMAP_DEFAULT = ipyleaflet.basemaps.OpenStreetMap.HOT
CENTER_DEFAULT = (35.7004, -105.9136)
ZOOM_DEFAULT = 9


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


    def _build_bq_figure(self, x, y, color):
        x_scale = bq.LinearScale()
        y_scale = bq.LinearScale()

        x_axis = bq.Axis(scale=x_scale, tick_values=None, num_ticks=3)
        y_axis = bq.Axis(scale=y_scale, tick_values=None, num_ticks=0, orientation='vertical', visible=False)

        line = bq.Lines(x=x, y=y, scales={'x': x_scale, 'y': y_scale}, colors=[color])

        fig = bq.Figure(title=color, marks=[line], axes=[x_axis, y_axis],
                        fig_margin={'top': 30, 'bottom': 30, 'left': 30, 'right': 30})
        fig.layout.width = '200px'
        fig.layout.height = '200px'

        return fig


    def _compute_hist(self, event):
        bounds = self.map.bounds
        bands, _, _ = self._get_band_parms()
        scale = ZOOM_TO_SCALE[self.map.zoom]
        
        hist = self.s2.compute_hist(bounds, bands, scale)
        colors = ['red', 'green', 'blue']
        
        figs = list()
        for bidx, band in enumerate(bands):
            hist_data = hist[band]
            color = colors[bidx]

            fig = self._build_bq_figure(hist_data[0], hist_data[1], color)
            figs.append(fig)

        figures = ipywidgets.HBox(figs)
        hist_control = ipyleaflet.WidgetControl(widget=figures, position='bottomleft')
        self.map.add_control(hist_control)


    
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
        self.histogram_button.on_click(self._compute_hist)

        #self.histogram_figures = list()
        #self.histogram_figures.append(plt.figure(figsize=(1,1)))
        #self.histogram_figures.append(plt.figure(figsize=(1,1)))
        #self.histogram_figures.append(plt.figure(figsize=(1,1)))
        #self.histogram_figure = ipywidgets.VBox(self.histogram_figures)
        #self.histogram_figure.layout.display = 'none'

        self.indiv_band_buttons = ipywidgets.VBox(
            [self.band_presets,
             self.single_band,
             self.gray_band_pane,
             self.single_band_panes[0],
             self.single_band_panes[1],
             self.single_band_panes[2],
             self.histogram_button]
             #self.histogram_figure]
        )
        
        self.indiv_band_buttons.layout.display = 'none'
        self.gray_band_pane.layout.visibility = 'hidden'

        band_button_control = ipyleaflet.WidgetControl(
            widget=self.band_button,
            position='topleft'
        )
#
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
            continuous_update=False,
            disabled=False
        )
        self.s2_date_start.observe(self._s2_observe)

        self.s2_date_end = ipywidgets.DatePicker(
            description='End',
            value=datetime.datetime(2020, 8, 1),
            continuous_update=False,
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

        
