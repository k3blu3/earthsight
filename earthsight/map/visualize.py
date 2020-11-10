'''
visualize.py

Visualize class definition that builds all widgets for Visualize pane
'''


import ipyleaflet as ipyl
import ipywidgets as ipyw


class Visualize:
    def __init__(self, m, layers):
        self.map = m
        self.layers = layers
        
        self._build_viz_button()
        self._build_viz_pane()

        self._add_controls()


    # -------------- #
    # -- CONTROLS -- #
    # -------------- #
    def _add_controls(self):
        vbc = ipyl.WidgetControl(
            widget=self.viz_button,
            position='topleft'
        )

        self.map.add_control(vbc)

        vpc = ipyl.WidgetControl(
            widget=self.viz_pane,
            position='topleft'
        )

        self.map.add_control(vpc)


    # ------------------ #
    # -- INTERACTIONS -- #
    # ------------------ #
    def _interact_viz_button(self, b):
        if self.viz_button.button_style == 'info':
            self.viz_button.button_style = 'success'
            self.viz_pane.layout.display = ''
        else:
            self.viz_button.button_style = 'info'
            self.viz_pane.layout.display = 'none'


    def _interact_band_presets(self, change):
        preset = self.band_presets.value
        layer = self.layers.get_selected()

        # TODO: pulls from SELECTED layer
        band_names, band_los, band_his = layer.img_src.get_band_presets()[preset]

        if len(band_names) == 1:
            self.single_band.value = True
        else:
            self.single_band.value = False

        for idx, (band_name, band_lo, band_hi) in enumerate(zip(band_names, band_los, band_his)):
            band = layer.img_src.bands.get(band_name)
            band.set_range(band_lo, band_hi)

            self.band_selectors[idx].value = band.get_name()
            self.band_sliders[idx].value = band.get_range()
            self.band_sliders[idx].min = band.get_min()
            self.band_sliders[idx].max = band.get_max()


    def _interact_single_band(self, change):
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


    def _interact_band_change(self, change):
        layer = self.layers.get_selected()

        band_names = self._get_current_bands()
        viz_params = self._get_viz_params(band_names)
        
        layer.img_src.update_viz(viz_params)
        layer.update()


    def _get_current_bands(self):
        band_names = list()
        layer = self.layers.get_selected()

        for band_selector, band_slider in zip(self.band_selectors, self.band_sliders):
            band_name = band_selector.value
            
            band = layer.img_src.bands.get(band_name)
            band.set_range(band_slider.value[0], band_slider.value[1])

            if self.single_band.value == True:
                break

            band_names.append(band_name)

        return band_names


    def _get_viz_params(self, band_names):
        band_los = list()
        band_his = list()
        layer = self.layers.get_selected()

        for band_name in band_names:
            band = layer.img_src.bands.get(band_name)
            lo, hi = band.get_range()

            band_los.append(lo)
            band_his.append(hi)

        viz_params = {'min': band_los,
                      'max': band_his,
                      'bands': band_names}

        return viz_params


    # ------------- #
    # -- WIDGETS -- #
    # ------------- #
    def _build_viz_button(self):
        button_layout = ipyw.Layout(width='auto', height='auto')
        viz_button = ipyw.Button(
            description='',
            icon='eye',
            button_style='info',
            tooltip='Configure visualization options',
            layout=button_layout
        )

        viz_button.on_click(self._interact_viz_button)

        self.viz_button = viz_button


    def _build_viz_pane(self):
        layer = self.layers.get_selected()

        band_preset_options = layer.img_src.get_band_presets().keys()
        band_presets = ipyw.Select(
            options=band_preset_options,
            value=list(band_preset_options)[0],
            description='see in',
            continuous_update=False
        )

        band_presets.observe(self._interact_band_presets, names='value')

        single_band = ipyw.Checkbox(
            value=False,
            description='single band',
            continuous_update=False
        )

        single_band.observe(self._interact_single_band, names='value')

        # TODO: band defaults should not live here in widget initialization
        all_band_names = layer.img_src.get_band_defs().keys()
        colors = ['red', 'green', 'blue']
        defaults = ['B4', 'B3', 'B2']
        band_selectors = list()
        band_sliders = list()
        for color, default in zip(colors, defaults):
            band_selector = ipyw.Dropdown(
                options=all_band_names,
                value=default,
                description=color,
                continuous_update=False
            )

            band_slider = ipyw.IntRangeSlider(
                value=[500, 3500],
                min=0,
                max=10000,
                step=1,
                continuous_update=False,
                orientation='horizontal',
                readout=True,
                readout_format='d'
            )

            band_selectors.append(band_selector)
            band_sliders.append(band_slider)

        band_panes = list()
        for band_selector, band_slider in zip(band_selectors, band_sliders):
            band_pane = ipyw.HBox(
                [
                    band_selector,
                    band_slider
                ]
            )
            band_panes.append(band_pane)

        for band_selector, band_slider in zip(band_selectors, band_sliders):
            band_selector.observe(self._interact_band_change, names='value')
            band_slider.observe(self._interact_band_change, names='value')

        viz_pane = ipyw.VBox(
            [
                band_presets,
                single_band,
                band_panes[0],
                band_panes[1],
                band_panes[2]
            ]
        )

        self.band_presets = band_presets
        self.single_band = single_band
        self.band_selectors = band_selectors
        self.band_sliders = band_sliders
        self.band_panes = band_panes
        self.viz_pane = viz_pane

        # don't display until button is pressed
        self.viz_pane.layout.display = 'none'
