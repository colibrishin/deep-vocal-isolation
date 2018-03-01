#!/usr/bin/python3
import numpy as np
from hashlib import md5

from config import Config


class Normalizer(object):
    def __init__(self):
        self.config = Config()
        self.normalizer = self.config.normalizer
        self.params = self.config.normalizer_params

    def get(self, both=True):
        function = getattr(self, self.normalizer)
        if self.params:
            params = eval(self.params)
        else:
            params = {}
        if both:
            def normalize_all(in_mashup, in_acapella):
                mashup = in_mashup.copy()
                acapella = in_acapella.copy()
                for i in range(len(mashup)):
                    mashup[i], norm = function(mashup[i], **params)
                    acapella[i], _ = function(acapella[i], norm=norm, **params)
                return mashup, acapella
            return normalize_all
        else:
            def normalize(matrix, norm=None):
                return function(matrix.copy(), norm=norm, **params)
            return normalize

    def get_reverse(self):
        function = getattr(self, "reverse_%s" % self.normalizer)

        def denormalize(matrix, norm):
            return function(matrix.copy(), norm)
        return denormalize

    def __hash__(self):
        config = self.normalizer + ":" + self.params
        val = md5(config.encode()).hexdigest()
        return int(val, 16)

    def dummy(self, matrix, norm=None):
        return matrix, 1

    def reverse_dummy(self, matrix, norm):
        return matrix

    def percentile(self, matrix, percentile, norm=None):
        if norm is not None:
            matrix /= norm
            return matrix, norm
        else:
            norm = np.percentile(matrix, percentile)
            # do not scale to range 0 - 1, if most of the data is close to 0
            if norm < 10e-5:
                norm = 1
            matrix /= norm
        return matrix, norm

    def reverse_percentile(self, matrix, norm):
        matrix *= norm
        return matrix