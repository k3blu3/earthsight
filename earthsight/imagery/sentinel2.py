'''
sentinel2.py

Sentinel-2 class definition that provides imagery on-demand via GEE
'''


import ee

from earthsight.imagery.bands import Bands
from earthsight.utils.gee import (image_to_tiles,
                                  bounds_to_geom)


S2_COLLECTION_IDS = ['COPERNICUS/S2',
                     'COPERNICUS/S2_CLOUD_PROBABILITY']


S2_MAX_CLOUD_PROBABILITY = 65


S2_BAND_DEFS = {
    'B1': (0, 10000),
    'B2': (0, 10000),
    'B3': (0, 10000),
    'B4': (0, 10000),
    'B5': (0, 10000),
    'B6': (0, 10000),
    'B7': (0, 10000),
    'B8': (0, 10000),
    'B8A': (0, 10000),
    'B9': (0, 10000),
    'B10': (0, 10000),
    'B11': (0, 10000),
    'B12': (0, 10000),
    'probability': (0, 100),
}


S2_BAND_PRESETS = {
    'true color': (['B4', 'B3', 'B2'],
                   [500, 500, 500], # lo
                   [3500, 3500, 3500]), # hi
    'color infrared': (['B8', 'B4', 'B3'],
                       [500, 500, 500],
                       [3500, 3500, 3500]),
    'short-wave infrared': (['B12', 'B8A', 'B4'],
                            [500, 500, 500],
                            [7500, 3500, 3500]),
    'agriculture': (['B11', 'B8', 'B2'],
                    [500, 500, 500],
                    [3500, 3500, 3500]),
    'geology': (['B12', 'B11', 'B8'],
                [500, 500, 500],
                [3500, 3500, 3500]),
    'bathymetric': (['B4', 'B3', 'B1'],
                    [500, 500, 500],
                    [3500, 3500, 3500]),
    'clouds': (['probability'],
               [0],
               [100]),
}


S2_BANDS = Bands()
for key in S2_BAND_DEFS.keys():
    name = key
    min_val, max_val = S2_BAND_DEFS[key]
    S2_BANDS.add(name, min_val, max_val)


class Sentinel2:
    def __init__(self,
                 collection_ids=S2_COLLECTION_IDS,
                 bands=S2_BANDS,
                 band_presets=S2_BAND_PRESETS):
        self.collection_ids = collection_ids
        self.bands = bands
        self.band_presets = band_presets

        self.ic = None
        self.img = None
        self.viz_params = None


    def _build_ic(self):
        # define S2 and S2 cloud probability image collections
        s2 = ee.ImageCollection(self.collection_ids[0])
        s2cloud = ee.ImageCollection(self.collection_ids[1])

        # join collections
        s2joined = ee.Join.saveFirst('cloud_mask').apply(
            primary=s2,
            secondary=s2cloud,
            condition=ee.Filter.equals(
                leftField='system:index',
                rightField='system:index'
            )
        )

        # add probability band into the original S2 image collection
        s2combined = ee.ImageCollection(s2joined).map(
            lambda img: img.addBands(
                img.get('cloud_mask')
            )
        )

        return s2combined


    def _ic_to_image(self, temporal_op):
        if temporal_op == 'mean':
            self.img = self.ic.mean()
        elif temporal_op == 'min':
            self.img = self.ic.min()
        elif temporal_op == 'max':
            self.img = self.ic.max()
        elif temporal_op == 'median':
            self.img = self.ic.median()
        elif temporal_op == 'mosaic':
            self.img = self.ic.mosaic()

    
    def _filter_date(self, start_datetime, end_datetime):
        self.ic = self.ic.filterDate(start_datetime, end_datetime)

    
    def _filter_clouds(self, cloudy_pixel_pct):
        cloud_filt = ee.Filter.lte('CLOUDY_PIXEL_PERCENTAGE', cloudy_pixel_pct)
        self.ic = self.ic.filter(cloud_filt)


    def _mask_clouds(self):
        self.ic = self.ic.map(self.__edge_mask)
        self.ic = self.ic.map(self.__cloud_mask)


    def __cloud_mask(self, img):
        clouds = ee.Image(img.get('cloud_mask')).select('probability')
        clouds_mask = clouds.lt(S2_MAX_CLOUD_PROBABILITY)
        
        return img.updateMask(clouds_mask)


    def __edge_mask(self, img):
        b9_mask = img.select('B9').mask()
        b8a_mask = img.select('B8A').mask()
        edge_mask = b9_mask.updateMask(b8a_mask)

        return img.updateMask(edge_mask)


    def compute_hist(self, bounds, band_names, scale):
        roi = bounds_to_geom(bounds)
        hist_img = self.img.select(band_names)
        hist = hist_img.reduceRegion(
            reducer=ee.Reducer.histogram(),
            geometry=roi,
            scale=scale,
            bestEffort=True
        )

        # retrive histogram as list
        hist_bands = hist.keys().getInfo()
        hist_list = hist.values().getInfo()
        hist_dict = dict()
        for band_name in band_names:
            band_idx = hist_bands.index(band_name)
            hist_dict[band] = (hist_list[band_idx]['bucketMeans'],
                               hist_list[band_idx]['histogram'])

        return hist_dict


    def update_ic(self, start_datetime, end_datetime, cloudy_pixel_pct, cloud_mask, temporal_op):
        self.ic = self._build_ic()
        self._filter_clouds(cloudy_pixel_pct)
        
        if cloud_mask:
            self._mask_clouds()

        self._filter_date(start_datetime, end_datetime)
        self._ic_to_image(temporal_op)


    def update_viz(self, viz_params):
        self.viz_params = viz_params


    def get_url(self):
        url = image_to_tiles(self.img, self.viz_params)
        return url

    
    def get_band_defs(self):
        return S2_BAND_DEFS


    def get_band_presets(self):
        return S2_BAND_PRESETS



