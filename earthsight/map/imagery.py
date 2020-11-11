'''
imagery.py

Imagery class definition that builds all widgets for Imagery pane
'''


from datetime import datetime
import ipywidgets as ipyw
import ipyleaflet as ipyl


class Imagery:
    def __init__(self, m, layers):
        self.map = m
        self.layers = layers

        self._build_img_button()
        self._build_img_pane()

        self._add_controls()

    
    # -------------- #
    # -- CONTROLS -- #
    # -------------- #
    def _add_controls(self):
        ibc = ipyl.WidgetControl(
            widget=self.img_button,
            position='topleft'
        )

        self.map.add_control(ibc)

        ipc = ipyl.WidgetControl(
            widget=self.img_pane,
            position='topleft'
        )

        self.map.add_control(ipc)


    # ------------------ #
    # -- INTERACTIONS -- #
    # ------------------ #
    def _interact_img_button(self, b):
        if self.img_button.button_style == 'info':
            self.img_button.button_style= 'success'
            self.img_pane.layout.display = ''
        else:
            self.img_button.button_style = 'info'
            self.img_pane.layout.display = 'none'


    def _interact_img_pane(self, change):
        layer = self.layers.get_selected()

        start_datetime = self.date_start.value.strftime('%Y-%m-%d')
        end_datetime = self.date_end.value.strftime('%Y-%m-%d')
        cloudy_pixel_pct = self.cloudy_pixel.value
        cloud_mask = self.cloud_mask.value
        temporal_op = self.temporal_op.value

        layer.img_src.img_params.set(
            start_datetime,
            end_datetime,
            cloudy_pixel_pct,
            cloud_mask,
            temporal_op
        )

        layer.update()


    # ------------- #
    # -- WIDGETS -- #
    # ------------- #
    def _build_img_button(self):
        button_layout = ipyw.Layout(width='auto', height='auto')
        img_button = ipyw.Button(
            description='',
            icon='globe',
            button_style='info',
            tooltip='Configure imagery options',
            layout=button_layout
        )

        img_button.on_click(self._interact_img_button)

        self.img_button = img_button


    def _build_img_pane(self):
        layer = self.layers.get_selected()

        # pick start date
        start_datetime = layer.img_src.img_params.get_start_datetime()
        date_start = ipyw.DatePicker(
            description='start',
            value=datetime.strptime(start_datetime, '%Y-%m-%d'),
            continuous_update=False,
        )

        # pick end date
        end_datetime = layer.img_src.img_params.get_end_datetime()
        date_end = ipyw.DatePicker(
            description='end',
            value=datetime.strptime(end_datetime, '%Y-%m-%d'),
            continuous_update=False,
        )

        # select cloud fraction
        cloudy_pixel_pct = layer.img_src.img_params.get_cloudy_pixel_pct()
        cloudy_pixel = ipyw.IntSlider(
            value=cloudy_pixel_pct,
            min=0,
            max=100,
            step=1,
            description='cloudy',
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d'
        )

        # mask clouds
        cloud_mask = layer.img_src.img_params.get_cloud_mask()
        cloud_mask = ipyw.Checkbox(
            value=cloud_mask,
            description='mask clouds',
            continuous_update=False
        )

        # select how to composite
        temporal_op = layer.img_src.img_params.get_temporal_op()
        temporal_op = ipyw.Dropdown(
            options=['mean', 'min', 'max', 'median', 'mosaic'],
            value=temporal_op,
            description='show',
            continuous_update=False
        )

        # on a change, we will update the image collection for the imagery source
        date_start.observe(self._interact_img_pane, names='value')
        date_end.observe(self._interact_img_pane, names='value')
        cloudy_pixel.observe(self._interact_img_pane, names='value')
        cloud_mask.observe(self._interact_img_pane, names='value')
        temporal_op.observe(self._interact_img_pane, names='value')

        img_pane = ipyw.VBox(
            [
                date_start,
                date_end,
                cloudy_pixel,
                cloud_mask,
                temporal_op
            ]
        )
        
        self.date_start = date_start
        self.date_end = date_end
        self.cloudy_pixel = cloudy_pixel
        self.cloud_mask = cloud_mask
        self.temporal_op = temporal_op
        self.img_pane = img_pane

        # default display is that it is not shown unless img button is clicked
        self.img_pane.layout.display = 'none'
