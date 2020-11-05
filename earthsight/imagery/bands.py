'''
bands.py

Class definition for Band and Bands, which provide a common interface for interacting with band data
'''


class Bands:
    def __init__(self):
        self.bands = list()


    def add(self, name, min_val, max_val):
        band = Band(name, min_val, max_val)
        self.bands.append(band)


    def get(self, name):
        this_band = None
        for band in self.bands:
            if band.get_name() == name:
                this_band = band
                break

        return this_band


class Band:
    def __init__(self, name, min_val, max_val):
        self.name = name
        self.min_val = min_val
        self.max_val = max_val

        self.lo_val = min_val
        self.hi_val = max_val

    
    def set_range(self, lo_val, hi_val):
        self.lo_val = lo_val
        self.hi_val = hi_val


    def get_range(self):
        return (self.lo_val, self.hi_val)


    def get_min(self):
        return self.min_val


    def get_max(self):
        return self.max_val


    def get_name(self):
        return self.name

