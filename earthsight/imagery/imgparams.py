'''
imgparams.py

Class definition for ImgParams, which provides a common interface for setting imagery parameters
'''


class ImgParams:
    def __init__(self):
        '''
        container that represents common imagery parameters
        '''
        self.start_datetime = None
        self.end_datetime = None
        self.cloudy_pixel_pct = None
        self.cloud_mask = None
        self.temporal_op = None


    def set(self, start_datetime, end_datetime, cloudy_pixel_pct, cloud_mask, temporal_op):
        '''
        set image parameters that define how an image is constructed
        '''
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime
        self.cloudy_pixel_pct = cloudy_pixel_pct
        self.cloud_mask = cloud_mask
        self.temporal_op = temporal_op


    # ------------- #
    # -- GETTERS -- #
    def get_start_datetime(self):
        return self.start_datetime


    def get_end_datetime(self):
        return self.end_datetime


    def get_cloudy_pixel_pct(self):
        return self.cloudy_pixel_pct

    
    def get_cloud_mask(self):
        return self.cloud_mask


    def get_temporal_op(self):
        return self.temporal_op
