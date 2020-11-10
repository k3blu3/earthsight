'''
histogram.py

Histogram class definition that builds all widgets for Histogram pane
'''


import ipywidgets as ipyw
import ipyleaflet as ipyl


class Histogram:
    def __init__(self, m, layers):
        self.map = m
        self.layers = layers

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
        if self.hist_button.button_style == 'info':
            self.hist_button.button_style = 'warning'

            self._build_hist_pane()

            # add hist pane control directly to map
            # TODO: this is kind of ugly
            self.controls.hist_control = ipyl.WidgetControl(
                widget=self.hist_pane,
                position='topleft'
            )
            self.map.add_control(self.hist_control)

            self.hist_button.button_style = 'success'
        else:
            self.hist_button.button_style = 'info'
            [l.unlink() for l in self.hist_links]
            self.map.remove_control(self.controls.hist_control)


    def _get_hist_figure(self, x, y, color, bidx):
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
        layer = self.layers.get_selected()

        bounds = self.map.bounds
        # TODO:
        band_names = self.get_current_bands()
        scale = ZOOM_TO_SCALE[self.map.zoom]
    
        hist = layer.img_src.compute_hist(bounds, band_names, scale)

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
