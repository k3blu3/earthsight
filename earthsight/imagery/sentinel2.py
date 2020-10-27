'''
sentinel2.py

Sentinel-2 class definition that provides imagery on-demand via GEE
'''


import ee

from earthsight.utils.gee import image_to_tiles


S2_COLLECTION_IDS = ['COPERNICUS/S2',
                     'COPERNICUS/S2_CLOUD_PROBABILITY']


S2_BANDS = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6',
            'B7', 'B8', 'B8A', 'B9', 'B10', 'B11', 'B12',
            'probability'] # cloud probability


S2_COLOR_PRESETS = {
    'True Color': (['B4', 'B3', 'B2'],
                   [0, 0, 0],
                   [3000, 3000, 3000]),
    'Vegetation': (['B8', 'B4', 'B3'],
                   [0, 0, 0],
                   [3000, 3000, 3000]),
    'Urban': (['B12', 'B11', 'B4'],
              [0, 0, 0],
              [3000, 3000, 3000]),
    'Infrared': (['B12', 'B8A', 'B4'],
                 [0, 0, 0],
                 [3000, 3000, 3000])
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

        # join them with new cloud mask band
        s2joined = ee.Join.saveFirst('cloud_mask').apply(
            primary=s2,
            secondary=s2cloud,
            condition=ee.Filter.equals(leftField='system:index',
                                       rightField='system:index')
        )

        return ee.ImageCollection(s2joined)


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


    def update(self, start_datetime, end_datetime, cloudy_pixel_pct, cloud_mask, temporal_op):
        self.ic = self._build_ic()
        self._filter_clouds(cloudy_pixel_pct)
        
        if cloud_mask:
            self._mask_clouds()

        self._filter_date(start_datetime, end_datetime)
        self._ic_to_image(temporal_op)


    def visualize(self, preset):
        bands, mins, maxs = S2_COLOR_PRESETS[preset]
        vis_params = {'min': mins,
                      'max': maxs,
                      'bands': bands}

        return image_to_tiles(self.img, vis_params)
        




