'''
layer.py

Class definition for Layer, which provide a common interface for interacting with map layers
'''


import ipyleaflet as ipyl
import ipywidgets as ipyw



class Layers:
    def __init__(self, m, widgets):
        self.map = m

        self.layers = list() # list of type Layer
        
        self.widgets = None
        self.widgets.layer_button = None
        self.widgets.layer_pane = None


    def add_layer(self, name, idx, img_src):
        layer = Layer(name, idx, img_src)
        self.map.add_layer(layer.get_map_layer())
        self.layers.append(layer)
        

    def get(self, idx):
        this_layer = None
        for layer in self.layers:
            if layer.idx == idx:
                selected_layer = layer

        return this_layer


    # ------------- #
    # -- WIDGETS -- #
    # ------------- #
    def _build_layer_button(self):
        layout = ipyw.Layout(width='auto', height='auto', border='solid')
        layer_button = ipyw.Button(
            description='',
            icon='layer-group',
            button_style='info',
            tooltip='select, add and remove map layers',
            layout=layout
        )

        self.widgets.layer_button = layer_button

    
    def _build_layer_window(self):
        basemaps = BASEMAPS.keys()
        layout = ipyw.Layout(width='auto', height='auto', border='solid')
        basemap_selector = ipyw.Dropdown(
            options=basemaps,
            value=basemaps[0],
            description='basemap',
            layout=layout,
            continuous_update=False
        )

        basemap_selector.observe(self._interact_basemap, names='value')

        layer_add = ipyw.Button(
            description='',
            icon='plus',
            button_style='success',
            tooltip='add new layer',
            layout=layout
        )

        layer_add.on_click(self.interact_layer_add)

        top_pane = ipyw.HBox([basemap_selector, layer_add])
        layer_window = ipyw.VBox([top_pane, [l.widgets.layer_pane for l in self.layers]])

        self.layer_window = layer_window
        self.layer_window.layout.display = 'none'
        



class Layer:
    def __init__(self, name, idx, img_src, selected=True, active=True):
        self.name = name
        self.idx = idx
        self.img_src = img_src

        self.url = None
        self.map_layer = None

        self.selected = True
        self.active = True

        self.widgets = None
        self.widgets.layer_text = None
        self.widgets.layer_remove = None
        self.widgets.layer_pane = None
        
        self.create()


    def set_url(self):
        url = self.img_src.get_url()
        return url


    def create_map_layer(self, name):
        self.map_layer = ipyl.TileLayer(url=self.url, name=name)
        return map_layer


    def update(self):
        url = self.img_src.get_url()
        self.map_layer.url = url


    def remove(self):
        self.map.remove_layer(self.map_layer)

    # ------------- #
    # -- WIDGETS -- #
    # ------------- #
    def _interact_layer_text(self, change):
        self.name = change['value']


    def _interact_layer_remove(self, change):
        # send a signal to update all layers.
        # this current layer will be removed
        pass
        


    def _build_single_layer(self):
        layout = ipyw.Layout(width='auto', height='auto', border='solid')
        layer_text = ipyw.Text(
            value='new layer',
            placeholder='type something',
            description='name'
        )

        layer_text.observe(self.interact_layer_text, names='value')

        layer_remove = ipyw.Button(
            description='',
            icon='trash-alt',
            button_style='danger',
            tooltip='remove map layer',
            layout=layout
        )

        layer_remove.observe(self.interact_layer_remove, names='value')

        layer_pane = ipyw.HBox([layer_text, layer_remove])

        self.widgets.layer_text = layer_text
        self.widgets.layer_remove = layer_remove
        self.widgets.layer_pane = layer_pane
