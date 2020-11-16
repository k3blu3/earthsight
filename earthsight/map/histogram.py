'''
histogram.py

Histogram class definition that builds all widgets for Histogram pane
'''


import bqplot as bq
import ipywidgets as ipyw
import ipyleaflet as ipyl

from earthsight.utils.constants import ZOOM_TO_SCALE


class Histogram:
    def __init__(self, m, layers, band_sliders):
        '''
        container for histogram pane on map
        '''
        self.map = m
        self.layers = layers
        self.band_sliders = band_sliders

        self._build_hist_button()
        self._add_controls()


    # -------------- #
    # -- CONTROLS -- #
    # -------------- #
    def _add_controls(self):
        hbc = ipyl.WidgetControl(
            widget=self.hist_button,
            position='topleft'
        )

        self.map.add_control(hbc)


    # ------------------ #
    # -- INTERACTIONS -- #
    # ------------------ #
    def _interact_hist_button(self, b):
        '''
        compute a histogram and show result when pressed
        '''
        if self.hist_button.button_style == 'info':
            self.hist_button.button_style = 'warning'

            self._build_hist_pane()

            # add hist pane control directly to map
            # TODO: this is kind of ugly
            self.hist_control = ipyl.WidgetControl(
                widget=self.hist_pane,
                position='topleft'
            )
            self.map.add_control(self.hist_control)

            self.hist_button.button_style = 'success'
        else:
            self.hist_button.button_style = 'info'
            [l.unlink() for l in self.hist_links]
            self.map.remove_control(self.hist_control)


    def _get_hist_figure(self, x, y, color, bidx):
        '''
        get a bqplot histogram figure with data and interactive sliders
        '''
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
    def _build_hist_button(self):
        '''
        build histogram button which computes a histogram of selected bands
        '''
        button_layout = ipyw.Layout(width='auto', height='auto')
        hist_button = ipyw.Button(
            description='',
            icon='chart-bar',
            button_style='info',
            tooltip='Compute histogram across selected bands',
            layout=button_layout
        )

        hist_button.on_click(self._interact_hist_button)

        self.hist_button = hist_button


    def _build_hist_pane(self):
        '''
        build histogram pane which contains interactive histogram figures
        '''
        layer = self.layers.get_selected()

        bounds = self.map.bounds
        scale = ZOOM_TO_SCALE[self.map.zoom]
    
        hist = layer.img_src.compute_hist(bounds, scale)

        band_names = layer.img_src.active_bands
        if len(band_names) == 1:
            colors = ['black']
        else:
            colors = ['red', 'green', 'blue']

        self.hist_figs = list()
        self.hist_links = list()
        for bidx, band in enumerate(band_names):
            hist_data = hist[band]
            color = colors[bidx]

            hist_fig = self._get_hist_figure(hist_data[0], hist_data[1], color, bidx)
            # TODO: these links are buggy
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
