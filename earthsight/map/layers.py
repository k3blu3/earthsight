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

        # throw on a default layer
        self.add(DEFAULT_LAYER_NAME, DEFAULT_IMG_SRC)

        self._build_layer_button()
        self._build_layer_window()

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

        lwc = ipyl.WidgetControl(
            widget=self.layer_window,
            position='bottomright'
        )

        self.map.add_control(lwc)


    # ------------------ #
    # -- INTERACTIONS -- #
    # ------------------ #
    def _interact_layer_button(self, b):
        if self.layer_button.button_style == 'info':
            self.layer_button.button_style = 'success'
            self.layer_window.layout.display = ''
        else:
            self.layer_button.button_style = 'info'
            self.layer_window.layout.display = 'none'


    def _interact_layer_add(self, b):
        name = 'layer {}'.format(self.ctr)
        self.layers.add(name, Sentinel2())
        
        single_layer = self._build_single_layer()
        self.single_layers.append(single_layer)

        selection_option = str(self.ctr)
        self.selection_options.append(selection_option)
        self.selection_pane.value = selection_option


    def _interact_layer_remove(self, b):
        layer = self.layers.get_selected()
        self.layers.remove(layer)

    
    def _interact_basemap(self, change):
        basemap_eval = BASEMAPS[self.basemap_selector.value]
        self.map.basemap = eval('ipyl.basemaps.{}'.format(basemap_eval))


    def _interact_layer_active(self, change):
        for layer, single_layer in zip(self.layers. self.single_layers):
            active = single_layer.children[1].value
            layer.active = active
            if active:
                layer.create()
            else:
                layer.destroy()


    def _interact_selection_pane(self, change):
        for layer in self.layers:
            if layer.ctr == int(self.selection_pane.value):
                layer.selected = True
            else:
                layer.selected = False


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


    def _build_layer_window(self):
        basemaps = BASEMAPS.keys()
        layout = ipyw.Layout(width='auto', height='auto')
        basemap_selector = ipyw.Dropdown(
            options=basemaps,
            value=list(basemaps)[0],
            description='basemap',
            layout=layout,
            continuous_update=False
        )

        basemap_selector.observe(self._interact_basemap, names='value')

        layer_add = ipyw.Button(
            description='',
            icon='plus',
            button_style='success',
            tooltip='add layer',
            layout=layout
        )

        layer_add.on_click(self._interact_layer_add)

        layer_remove = ipyw.Button(
            description='',
            icon='minus',
            button_style='danger',
            tooltip='remove layer',
            layout=layout
        )

        layer_remove.on_click(self._interact_layer_remove)

        top_pane = ipyw.HBox([basemap_selector, layer_add, layer_remove])
            
        single_layers = list()
        for layer in self.layers:
            single_layer = self._build_single_layer(layer.name)
            single_layers.append(single_layer)

        selection_options = list()
        for layer in self.layers:
            selection_options.append(layer.ctr)

        selection_pane = ipyw.RadioButtons(
            options=selection_options,
            value=selection_options[0],
            description='select',
            layout=layout
        )

        selection_pane.observe(self._interact_selection_pane)
        
        layer_pane = ipyw.HBox(
            [
                selection_pane, 
                ipyw.VBox(single_layers)
            ]
        )

        layer_window = ipyw.VBox([top_pane, layer_pane])

        self.basemap_selector = basemap_selector
        self.layer_add = layer_add
        self.layer_remove = layer_remove
        self.top_pane = top_pane
        self.single_layers = single_layers
        self.selection_options = selection_options
        self.selection_pane = selection_pane
        self.layer_pane = layer_pane
        self.layer_window = layer_window

        # don't show until button is pressed
        self.layer_window.layout.display = 'none'
    
    
    def _build_single_layer(self, name=None):
        layout = ipyw.Layout(width='auto', height='auto')
        
        if name is None:
            name = 'New Layer {}'.format(self.layer_ctr)
        
        layer_text = ipyw.Text(
            value=name,
            placeholder='type something',
            description='name',
            layout=layout
        )

        layer_active = ipyw.Checkbox(
            value=True,
            description='',
            indent=False,
            layout=layout,
        )

        layer_active.observe(self._interact_layer_active, names='value')

        single_layer = ipyw.HBox(
            [
                layer_active,
                layer_text
            ]
        )

        return single_layer
        

class Layer:
    def __init__(self, name, ctr, img_src, m, selected=True, active=True):
        self.name = name
        self.ctr = ctr
        self.img_src = img_src
        self.map = m

        self.active = True
        self.selected = True
        
        self.map_layer = None


    def get_url(self):
        url = self.img_src.get_url()
        return url


    def create(self):
        url = self.get_url()
        self.map_layer = ipyl.TileLayer(url=url, name=self.name)
        self.map.add_layer(self.map_layer)


    def destroy(self):
        self.map.remove_layer(self.map_layer)
        self.map_layer = None


    def update(self):
        self.map_layer.url = self.get_url()
