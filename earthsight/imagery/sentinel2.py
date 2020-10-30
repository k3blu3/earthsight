'''
sentinel2.py

Sentinel-2 class definition that provides imagery on-demand via GEE
'''


import ee

from earthsight.utils.gee import (image_to_tiles,
                                  bounds_to_geom)


S2_COLLECTION_IDS = ['COPERNICUS/S2',
                     'COPERNICUS/S2_CLOUD_PROBABILITY']


S2_BANDS = [('B1', 0, 10000), 
            ('B2', 0, 10000), 
            ('B3', 0, 10000),
            ('B4', 0, 10000),
            ('B5', 0, 10000),
            ('B6', 0, 10000),
            ('B7', 0, 10000),
            ('B8', 0, 10000),
            ('B8A', 0, 10000),
            ('B9', 0, 10000),
            ('B10', 0, 10000),
            ('B11', 0, 10000),
            ('B12', 0, 10000),
            ('probability', 0, 100)] # cloud probability


S2_BAND_PRESETS = {
    'True Color': (['B4', 'B3', 'B2'],
                   [0, 0, 0],
                   [3000, 3000, 3000]),
    'Color Infrared': (['B8', 'B4', 'B3'],
                       [0, 0, 0],
                       [3000, 3000, 3000]),
    'Short-Wave Infrared': (['B12', 'B8A', 'B4'],
                            [0, 0, 0],
                            [7500, 3000, 3000]),
    'Agriculture': (['B11', 'B8', 'B2'],
                    [0, 0, 0],
                    [3000, 3000, 3000]),
    'Geology': (['B12', 'B11', 'B8'],
                [0, 0, 0],
                [3000, 3000, 3000]),
    'Bathymetric': (['B4', 'B3', 'B1'],
                    [0, 0, 0],
                    [3000, 3000, 3000]),
    'Clouds': (['probability'],
               [0],
               [100])
}


S2_MAX_CLOUD_PROBABILITY = 65


class Sentinel2:
    def __init__(self,
                 collection_ids=S2_COLLECTION_IDS,
                 bands=S2_BANDS):
        self.collection_ids = collection_ids
        self.bands = bands
        self.ic = None
        self.img = None


    def _build_ic(self):
        # define S2 and S2 cloud probability image collections
        s2 = ee.ImageCollection(self.collection_ids[0])
        s2cloud = ee.ImageCollection(self.collection_ids[1])

        # join collections
        s2joined = ee.Join.saveFirst('cloud_mask').apply(
            primary=s2,
            secondary=s2cloud,
            condition=ee.Filter.equals(leftField='system:index',
                                       rightField='system:index')
        )

        # add probability band into the original S2 image collection
        s2combined = ee.ImageCollection(s2joined).map(lambda img: img.addBands(img.get('cloud_mask')))

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


    def compute_hist(self, bounds, bands, scale):
        roi = bounds_to_geom(bounds)
        hist_img = self.img.select(bands)
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
        for band in bands:
            band_idx = hist_bands.index(band)
            hist_dict[band] = (hist_list[band_idx]['bucketMeans'],
                               hist_list[band_idx]['histogram'])

        return hist_dict


    def update(self, start_datetime, end_datetime, cloudy_pixel_pct, cloud_mask, temporal_op):
        self.ic = self._build_ic()
        self._filter_clouds(cloudy_pixel_pct)
        
        if cloud_mask:
            self._mask_clouds()

        self._filter_date(start_datetime, end_datetime)
        self._ic_to_image(temporal_op)


    def visualize(self, band_parms):
        bands, mins, maxs = band_parms
        vis_params = {'min': mins,
                      'max': maxs,
                      'bands': bands}

        return image_to_tiles(self.img, vis_params)


    def get_bands(self):
        return S2_BANDS


    def get_band_presets(self):
        return S2_BAND_PRESETS


        




