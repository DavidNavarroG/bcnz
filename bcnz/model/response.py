#!/usr/bin/env python
# encoding: UTF8

import ipdb
import os
import pdb
import numpy as np
from scipy.integrate import trapz
from scipy.interpolate import splev, splrep


class sed_filters(object):
    def find_sky_spl(self, conf):
        file_path = os.path.join(conf['data_dir'], conf['sky_spec'])
        x,y = np.loadtxt(file_path, unpack=True)

        return splrep(x,y)

    def find_response_spls(self, conf, filters):
        """Create response splines for different filters."""

        clight_AHz=2.99792458e18
        sky_spl = self.find_sky_spl(conf)

        spls, r_const, rlim, in_rD, in_skyD = {},{},{},{},{}
        d = os.path.join(conf['data_dir'], conf['filter_dir'])
        fmt = conf['res_fmt']
        for filter_name in filters:
            file_path = os.path.join(d, fmt.format(filter_name))
            x,y = np.loadtxt(file_path, unpack=True)

            # Determines the range where the filter curve is non-zero.
            # Cryptic, but works.
#            rlim[filter_name] = tuple(x[(y != 0).nonzero()[0][[0,-1]]])
            rlim[filter_name] = (x[0], x[-1])

            # Normalization and CCD effects.
            y2 = y*x
            #r_const[file_name] = 1./simps(y/x/x,x) / clight_AHz
            r_const[filter_name] = 1./trapz(y2/x/x,x) / clight_AHz
            spls[filter_name] = splrep(x, y2)
            in_rD[filter_name] = trapz(y/x, x)
            y_sky = splev(x, sky_spl)
            in_skyD[filter_name] = trapz(y*y_sky, x)

        in_r = np.array([in_rD[x] for x in filters])
        in_sky = np.array([in_skyD[x] for x in filters])

#        ipdb.set_trace()

        return rlim, r_const, spls, in_r, in_sky

    def _load_filters(self, conf, filters):
        """Load filters stored in ascii files."""

        print('Loading from ascii...')

        res = {}
        d = os.path.join(conf['data_dir'], conf['filter_dir'])
        fmt = conf['res_fmt']
        for fname in filters:
            file_path = os.path.join(d, fmt.format(fname))
            x,y = np.loadtxt(file_path, unpack=True)

            res[fname] = x,y

        return res

    def _load_seds(self, conf, seds):
        print('Loading SEDS')
        res = {}
        d = os.path.join(conf['data_dir'], conf['sed_dir'])
        for sed in seds:
            file_path = os.path.join(d, '%s.sed' % sed)
            x,y = np.loadtxt(file_path, unpack=True)

            res[sed] = x,y

        return res

    def find_sed_spls(self, conf, zdata, seds):
        """Create spectra splines."""

        sedD = zdata['sedsD'] if 'sedsD' in zdata else self._load_seds(conf, seds)

        spls = {}
        for sed in seds:
            spls[sed] = splrep(*sedD[sed])

        return spls

    def __call__(self, conf, zdata):
        filters = zdata['filters']
        seds = zdata['seds']

        filtersD = zdata['filtersD'] if 'filtersD' in zdata else self._load_filters(conf, filters)
        rlim, r_const, resp_spls,in_r,in_sky = self.find_response_spls(conf, filters)
        sed_spls = self.find_sed_spls(conf, zdata, seds)

        spl_data = {'resp_spls': resp_spls,
                    'sed_spls': sed_spls,
                    'rlim': rlim,
                    'r_const': r_const,
                    'max_type': len(seds) - 1,
                    'in_r': in_r,
                    'in_sky': in_sky}

        return spl_data
