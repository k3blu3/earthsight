'''
layer.py

Class definition for Layer, which provide a common interface for interacting with map layers
'''


import ipyleaflet as ipyl
import ipywidgets as ipyw

from earthsight.map.basemaps import BASEMAPS
from earthsight.imagery.sentinel2 import Sentinel2


DEFAULT_LAYER_NAME = 'Sentinel-2'
DEFAULT_IMG_SRC = Sentinel2()


class Layers:
    def __init__(self, m):
        self.map = m

        self.layers = list()

        self.ctr = 0

        self.add(DEFAULT_LAYER_NAME, DEFAULT_IMG_SRC)

        self._build_layer_button()
        self._build_top_pane()
        self._build_layer_window()
        self._update_selected()

        self._add_controls()


    def add(self, name, img_src):
        for layer in self.layers:
            layer.selected = False

        layer = Layer(name, self.ctr, img_src, self.map)
        self.layers.append(layer)
        self.ctr += 1


    def remove(self, layer):
        self.layers.remove(layer)
        

    def get(self, name):
        this_layer = None
        for layer in self.layers:
            if layer.idx == idx:
                selected_layer = layer

        return this_layer


    def get_selected(self):
        this_layer = None
        for layer in self.layers:
            if layer.selected == True:
                this_layer = layer
        
        return this_layer


    def get_active(self):
        these_layers = list()
        for layer in self.layers:
            if layer.active == True:
                these_layers.append(layer)

        return these_layers


    # -------------- #
    # -- CONTROLS -- #
    # -------------- #
    def _add_controls(self):
        lbc = ipyl.WidgetControl(
            widget=self.layer_button,
            position='bottomright'
        )

        self.map.add_control(lbc)


    # ------------------ #
    # -- INTERACTIONS -- #
    # ------------------ #
    def _interact_layer_button(self, b):
        if self.layer_button.button_style == 'info':
            self.layer_button.button_style = 'success'

            self.layer_control = ipyl.WidgetControl(
                widget=self.layer_window,
                position='bottomright'
            )
            self.map.add_control(self.layer_control)
        else:
            self.layer_button.button_style = 'info'
            self.map.remove_control(self.layer_control)



    def _interact_layer_add(self, b):
        name = 'layer {}'.format(self.ctr)
        self.add(name, Sentinel2())

        self.map.remove_control(self.layer_control)
        self._build_layer_window()
        self.layer_control = ipyl.WidgetControl(
            widget=self.layer_window,
            position='bottomright'
        )
        self.map.add_control(self.layer_control)

        self._update_selected()


    def _interact_layer_remove(self, b):
        self.remove(self.get_selected())

        self.map.remove_control(self.layer_control)
        self._build_layer_window()
        self.layer_control = ipyl.WidgetControl(
            widget=self.layer_window,
            position='bottomright'
        )
        self.map.add_control(self.layer_control)

        self._update_selected()

    
    def _interact_basemap(self, change):
        old_basemap = self.map.layers[0]
        basemap_eval = BASEMAPS[self.basemap_selector.value]
        basemap = eval('ipyl.basemaps.{}'.format(basemap_eval))
        self.map.add_layer(basemap)
        self.map.remove_layer(old_basemap)

    
    def _interact_layer_text(self, change):
        for layer, single_layer in zip(self.layers, self.single_layers):
            layer.name = single_layer.children[0].value


    def _interact_layer_active(self, change):
        for layer, single_layer in zip(self.layers, self.single_layers):
            active = single_layer.children[1].value
            layer.active = active
            if active:
                single_layer.children[1].button_style = 'info'
                layer.create()
            else:
                single_layer.children[1].button_style = ''
                layer.destroy()


    def _update_selected(self):
        layer_idx = len(self.layers) - 1
        for idx, (layer, single_layer) in enumerate(zip(self.layers, self.single_layers)):
            if idx == layer_idx:
                layer.selected = True
                single_layer.children[2].button_style = 'info'
            else:
                layer.selected = False
                single_layer.children[2].button_style = ''


    def _interact_layer_selected(self, b):
        layer_idx = int(b.tooltip) - 1
        for layer, single_layer in zip(self.layers, self.single_layers):
            if layer.ctr == layer_idx:
                layer.selected = True
                single_layer.children[2].button_style = 'info'
            else:
                layer.selected = False
                single_layer.children[2].button_style = ''


    # ------------- #
    # -- WIDGETS -- #
    # ------------- #
    def _build_layer_button(self):
        layout = ipyw.Layout(width='auto', height='auto')
        layer_button = ipyw.Button(
            description='',
            icon='layer-group',
            button_style='info',
            tooltip='select, add and remove map layers',
            layout=layout
        )

        layer_button.on_click(self._interact_layer_button)

        self.layer_button = layer_button


    def _build_top_pane(self):
        basemaps = BASEMAPS.keys()
        layout = ipyw.Layout(width='auto', height='auto')
        self.basemap_selector = ipyw.Dropdown(
            options=basemaps,
            value=list(basemaps)[0],
            description='basemap',
            continuous_update=False
        )

        self.basemap_selector.observe(self._interact_basemap, names='value')

        self.layer_add = ipyw.Button(
            description='',
            icon='plus',
            button_style='success',
            tooltip='add layer',
            layout=layout
        )

        self.layer_add.on_click(self._interact_layer_add)

        self.layer_remove = ipyw.Button(
            description='',
            icon='minus',
            button_style='danger',
            tooltip='remove layer',
            layout=layout
        )

        self.layer_remove.on_click(self._interact_layer_remove)

        self.top_pane = ipyw.HBox(
            [
                self.basemap_selector, 
                self.layer_add, 
                self.layer_remove
            ]
        )


    def _build_layer_window(self):
        self.single_layers = list()
        for layer in self.layers:
            self._build_single_layer(layer)
        self.layer_pane = ipyw.VBox(self.single_layers)

        self.layer_window = ipyw.VBox([self.top_pane, self.layer_pane])

    
    def _build_single_layer(self, layer):
        layout = ipyw.Layout(width='auto', height='auto')
        
        layer_text = ipyw.Text(
            value=layer.name,
            placeholder='type something',
            description='name',
        )

        layer_active = ipyw.ToggleButton(
            value=True,
            description='',
            layout=layout,
            button_style='info',
            tooltip='display layer on map',
            icon='eye'
        )

        layer_selected = ipyw.Button(
            description='',
            tooltip=str(layer.ctr + 1),
            button_style='',
            layout=layout,
            icon='check'
        )

        layer_text.observe(self._interact_layer_text, names='value')
        layer_active.observe(self._interact_layer_active, names='value')
        layer_selected.on_click(self._interact_layer_selected)

        single_layer = ipyw.HBox(
            [
                layer_text,
                layer_active,
                layer_selected
            ]
        )

        self.single_layers.append(single_layer)
        

class Layer:
    def __init__(self, name, ctr, img_src, m, selected=True, active=True):
        self.name = name
        self.ctr = ctr
        self.img_src = img_src
        self.map = m

        self.active = True
        self.selected = True
        
        self.map_layer = None

        self.create()


    def get_url(self):
        url = self.img_src.get_url()
        return url


    def create(self):
        url = self.get_url()
        self.map_layer = ipyl.TileLayer(url=url, name=self.name)
        self.map.add_layer(self.map_layer)


    def destroy(self):
        if self.map_layer is not None:
            self.map.remove_layer(self.map_layer)
            self.map_layer = None


    def update(self):
        self.img_src.update_ic()
        self.img_src.update_viz()
        self.map_layer.url = self.get_url()
