'''
earthwidgets.py

EarthWidgets class definition that builds all widgets that go on EarthMap
'''


import datetime
import ipyleaflet as ipyl
import ipywidgets as ipyw
import bqplot as bq


from earthsight.imagery.sentinel2 import Sentinel2
from earthsight.utils.constants import ZOOM_TO_SCALE


class EarthWidgets:
    def __init__(self, m):
        self.map = m
        self.imagery = Sentinel2()


    def update_layer(self):
        url = self.imagery.get_url()
        if len(self.map.layers) == 1:
            layer = ipyl.TileLayer(url=url, name='Sentinel-2')
            self.map.add_layer(layer)
        else:
            self.map.layers[-1].url = url


    # ------------------ #
    # -- INTERACTIONS -- #
    # ------------------ #
    def interact_img_button(self, b):
        if self.img_button.button_style == 'info':
            self.img_button.button_style= 'success'
            self.img_pane.layout.display = ''
        else:
            self.img_button.button_style = 'info'
            self.img_pane.layout.display = 'none'


    def interact_img_pane(self, change):
        start_datetime = self.date_start.value.strftime('%Y-%m-%d')
        end_datetime = self.date_end.value.strftime('%Y-%m-%d')
        cloudy_pixel_pct = self.cloudy_pixel.value
        cloud_mask = self.cloud_mask.value
        temporal_op = self.temporal_op.value

        self.imagery.img_params.set(
            start_datetime,
            end_datetime,
            self.cloudy_pixel.value,
            self.cloud_mask.value,
            self.temporal_op.value
        )

        self.imagery.update_ic()

        self.update_layer()


    def interact_viz_button(self, b):
        if self.viz_button.button_style == 'info':
            self.viz_button.button_style = 'success'
            self.viz_pane.layout.display = ''
        else:
            self.viz_button.button_style = 'info'
            self.viz_pane.layout.display = 'none'

    
    def interact_band_presets(self, change):
        preset = self.band_presets.value
        band_names, band_los, band_his = self.imagery.get_band_presets()[preset]

        if len(band_names) == 1:
            self.single_band.value = True
        else:
            self.single_band.value = False

        for idx, (band_name, band_lo, band_hi) in enumerate(zip(band_names, band_los, band_his)):
            band = self.imagery.bands.get(band_name)
            band.set_range(band_lo, band_hi)

            self.band_selectors[idx].value = band.get_name()
            self.band_sliders[idx].value = band.get_range()
            self.band_sliders[idx].min = band.get_min()
            self.band_sliders[idx].max = band.get_max()

    
    def interact_single_band(self, change):
        if self.single_band.value == True:
            self.band_panes[0].layout.display = ''
            self.band_selectors[0].description = 'gray'
            self.band_panes[1].layout.display = 'none'
            self.band_panes[2].layout.display = 'none'
        else:
            self.band_panes[0].layout.display = ''
            self.band_selectors[0].description = 'red'
            self.band_panes[1].layout.display = ''
            self.band_panes[2].layout.display = ''

        self.interact_band_change(None)

    
    def interact_band_change(self, change):
        band_names = self.get_current_bands()
        viz_params = self.get_viz_params(band_names)
        self.imagery.update_viz(viz_params)
        self.update_layer()
    

    def interact_hist_button(self, b):
        if self.hist_button.button_style == 'info':
            self.hist_button.button_style = 'warning'
            self.hist_button.description = 'Calculating...'

            self.build_hist_pane()

            # add hist pane control directly to map
            # TODO: this is kind of ugly
            self.hist_control = ipyl.WidgetControl(
                widget=self.hist_pane,
                position='topleft'
            )
            self.map.add_control(self.hist_control)

            self.hist_button.button_style = 'success'
            self.hist_button.description = 'Histogram'

        else:
            self.hist_button.button_style = 'info'
            [l.unlink() for l in self.hist_links]
            self.map.remove_control(self.hist_control)


    # ------------- #
    # -- GETTERS -- #
    # ------------- #
    def get_current_bands(self):
        band_names = list()
        for band_selector, band_slider in zip(self.band_selectors, self.band_sliders):
            band_name = band_selector.value
            band = self.imagery.bands.get(band_name)
            band.set_range(band_slider.value[0], band_slider.value[1])

            if self.single_band.value == True:
                break

            band_names.append(band_name)

        return band_names


    def get_viz_params(self, band_names):
        band_los = list()
        band_his = list()

        for band_name in band_names:
            band = self.imagery.bands.get(band_name)
            lo, hi = band.get_range()
            
            band_los.append(lo)
            band_his.append(hi)

        viz_params = {'min': band_los,
                      'max': band_his,
                      'bands': band_names}

        return viz_params

    
    def get_hist_figure(self, x, y, color, bidx):
        x_scale = bq.LinearScale()
        y_scale = bq.LinearScale()

        x_axis = bq.Axis(scale=x_scale, tick_values=None, num_ticks=3)
        y_axis = bq.Axis(
            scale=y_scale,
            tick_values=None,
            num_ticks=0,
            orientation='vertical',
            visible=False
        )

        line = bq.Lines(
            x=x,
            y=y,
            scales={
                'x': x_scale,
                'y': y_scale
            },
            colors=[color],
            selected_style={'opacity': '1'},
            unselected_style={'opacity': '0.2'}
        )

        fast_sel = bq.interacts.FastIntervalSelector(marks=[line], scale=x_scale, color='orange')

        fig = bq.Figure(
            title=color,
            marks=[line],
            axes=[x_axis, y_axis],
            fig_margin={
                'top': 40,
                'bottom': 40,
                'left': 40,
                'right': 40
            },
            interaction=fast_sel
        )
        fig.layout.width = '225px'
        fig.layout.height = '225px'

        return fig


    # ------------- #
    # -- WIDGETS -- #
    # ------------- #
    def build_img_button(self):
        self.img_button = ipyw.Button(
            description='Imagery',
            disabled=False,
            button_style='info',
            tooltip='Configure imagery options'
        )

        self.img_button.on_click(self.interact_img_button)


    def build_img_pane(self):
        # pick start date
        start_datetime = self.imagery.img_params.get_start_datetime()
        self.date_start = ipyw.DatePicker(
            description='start',
            value=datetime.datetime.strptime(start_datetime, '%Y-%m-%d'),
            continuous_update=False,
            disabled=False
        )

        # pick end date
        end_datetime = self.imagery.img_params.get_end_datetime()
        self.date_end = ipyw.DatePicker(
            description='end',
            value=datetime.datetime.strptime(end_datetime, '%Y-%m-%d'),
            continuous_update=False,
            disabled=False
        )

        # select cloud fraction
        cloudy_pixel_pct = self.imagery.img_params.get_cloudy_pixel_pct()
        self.cloudy_pixel = ipyw.IntSlider(
            value=cloudy_pixel_pct,
            min=0,
            max=100,
            step=1,
            description='cloudy',
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d'
        )

        # mask clouds
        cloud_mask = self.imagery.img_params.get_cloud_mask()
        self.cloud_mask = ipyw.Checkbox(
            value=cloud_mask,
            description='mask clouds',
            disabled=False,
            continuous_update=False
        )

        # select how to composite
        temporal_op = self.imagery.img_params.get_temporal_op()
        self.temporal_op = ipyw.Dropdown(
            options=['mean', 'min', 'max', 'median', 'mosaic'],
            value=temporal_op,
            description='show',
            disabled=False,
            continuous_update=False
        )

        # on a change, we will update the image collection for the imagery source
        self.date_start.observe(self.interact_img_pane, names='value')
        self.date_end.observe(self.interact_img_pane, names='value')
        self.cloudy_pixel.observe(self.interact_img_pane, names='value')
        self.cloud_mask.observe(self.interact_img_pane, names='value')
        self.temporal_op.observe(self.interact_img_pane, names='value')

        self.img_pane = ipyw.VBox(
            [
                self.date_start,
                self.date_end,
                self.cloudy_pixel,
                self.cloud_mask,
                self.temporal_op
            ]
        )

        # default display is that it is not shown unless img button is clicked
        self.img_pane.layout.display = 'none'


    def build_viz_button(self):
        self.viz_button = ipyw.Button(
            description='Visualize',
            disabled=False,
            button_style='info',
            tooltip='Configure visualization options'
        )
        
        self.viz_button.on_click(self.interact_viz_button)


    def build_viz_pane(self):
        band_preset_options = self.imagery.get_band_presets().keys()
        self.band_presets = ipyw.Select(
            options=band_preset_options,
            value=list(band_preset_options)[0],
            description='see in',
            disabled=False,
            continuous_update=False
        )

        self.band_presets.observe(self.interact_band_presets, names='value')

        self.single_band = ipyw.Checkbox(
            value=False,
            description='single band',
            disabled=False,
            continuous_update=False
        )

        self.single_band.observe(self.interact_single_band, names='value')

        all_band_names = self.imagery.get_band_defs().keys()

        # TODO: band defaults should not live here in widget initialization
        colors = ['red', 'green', 'blue']
        defaults = ['B4', 'B3', 'B2']
        self.band_selectors = list()
        self.band_sliders = list()
        for color, default in zip(colors, defaults):
            band_selector = ipyw.Dropdown(
                options=all_band_names,
                value=default,
                description=color,
                disabled=False,
                continuous_update=False
            )
            
            band_slider = ipyw.IntRangeSlider(
                value=[500, 3500],
                min=0,
                max=10000,
                step=1,
                disabled=False,
                continuous_update=False,
                orientation='horizontal',
                readout=True,
                readout_format='d'
            )

            self.band_selectors.append(band_selector)
            self.band_sliders.append(band_slider)

        self.band_panes = list()
        for band_selector, band_slider in zip(self.band_selectors, self.band_sliders):
            band_pane = ipyw.HBox(
                [
                    band_selector,
                    band_slider
                ]
            )
            self.band_panes.append(band_pane)

        for band_selector, band_slider in zip(self.band_selectors, self.band_sliders):
            band_selector.observe(self.interact_band_change, names='value')
            band_slider.observe(self.interact_band_change, names='value')

        self.viz_pane = ipyw.VBox(
            [
                self.band_presets,
                self.single_band,
                self.band_panes[0],
                self.band_panes[1],
                self.band_panes[2]
            ]
        )
        self.viz_pane.layout.display = 'none'

        self.interact_img_pane(None)
        self.interact_band_change(None)


    def build_hist_button(self):
        self.hist_button = ipyw.Button(
            description='Histogram',
            disabled=False,
            button_style='info',
            tooltip='Compute histogram across selected bands'
        )

        self.hist_button.on_click(self.interact_hist_button)


    def build_hist_pane(self):
        bounds = self.map.bounds
        band_names = self.get_current_bands()
        scale = ZOOM_TO_SCALE[self.map.zoom]

        hist = self.imagery.compute_hist(bounds, band_names, scale)

        if self.single_band.value == True:
            colors = ['black']
        else:
            colors = ['red', 'green', 'blue']

        self.hist_figs = list()
        self.hist_links = list()
        for bidx, band in enumerate(band_names):
            hist_data = hist[band]
            color = colors[bidx]

            hist_fig = self.get_hist_figure(hist_data[0], hist_data[1], color, bidx)
            hist_link = ipyw.jslink(
                (
                    self.band_sliders[bidx],
                    'value'
                ),
                (
                    hist_fig.interaction,
                    'selected'
                )
            )

            self.hist_figs.append(hist_fig)
            self.hist_links.append(hist_link)

        self.hist_pane = ipyw.HBox(self.hist_figs)
