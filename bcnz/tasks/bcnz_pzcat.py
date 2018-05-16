#!/usr/bin/env python
# encoding: UTF8

from IPython.core import debugger as ipdb
import os
import sys
import time
import numpy as np
import pandas as pd
import xarray as xr

from matplotlib import pyplot as plt

# Yes, this is not exactly nice ...
sys.path.append('/home/eriksen/code/bcnz/bcnz/tasks')
sys.path.append(os.path.expanduser('~/Dropbox/pauphotoz/bcnz/bcnz/tasks'))
import libpzqual

descr = {'odds_lim': 'Limit within to estimate the ODDS',
         'width_frac': 'Fraction used when estimating the pz_width'}

class bcnz_pzcat:
    """Catalogs for the photometric redshifts."""

    version = 1.03
    config = {'odds_lim': 0.0035,
              'width_frac': 0.01,
              'priors': 'none',
              'nsmooth': 5}

    def test(self, pz):
        from matplotlib import pyplot as plt

#        y1 = pz[0].sum(dim='ref_id')
#        y2 = pz[1].sum(dim='ref_id')
#        y3 = pz[2].sum(dim='ref_id')
#
#        from scipy.ndimage.filters import gaussian_filter
#        hmm = pz.sum(dim='ref_id')

        hmm = pz.sum(dim=['ref_id', 'chunk'])


        ipdb.set_trace()


    def entry(self, chi2):
        pz = np.exp(-0.5*chi2)
        pz_norm = pz.sum(dim=['chunk', 'z'])
        pz_norm = pz_norm.clip(1e-200, np.infty)

        pz = pz / pz_norm

#        self.test(pz)

        if self.config['priors'] == 'none':
            pass
        elif self.config['priors'] == 'chunk':
            prior_chunk = pz.sum(dim=['ref_id', 'z'])
            prior_chunk = prior_chunk / prior_chunk.sum()

            pz = pz*prior_chunk
            pz_norm = pz.sum(dim=['chunk', 'z'])
            pz = pz / pz_norm
        elif self.config['priors'] == 'both':
            prior_both = pz.sum(dim=['ref_id'])

            ipdb.set_trace()

            pz = pz*prior_both
            pz_norm = pz.sum(dim=['chunk', 'z'])
            pz = pz / pz_norm
        elif self.config['priors'] == 'test':
            from scipy.ndimage.filters import gaussian_filter
            prior_test = gaussian_filter(pz.sum(dim='ref_id'), [0., 10.])
            prior_test = xr.DataArray(prior_test, dims=('chunk', 'z'), \
                         coords={'chunk': pz['chunk'], 'z': pz.z})

            pz = pz*prior_test
            pz_norm = pz.sum(dim=['chunk', 'z'])
            pz = pz / pz_norm
        elif self.config['priors'] == 'test17':
            # Attempting chunk and z priors separately.
            from scipy.ndimage.filters import gaussian_filter

            prior_z = pz.sum(dim=['chunk', 'ref_id'])
            prior_z.values[:] = gaussian_filter(prior_z, self.config['nsmooth'])
            prior_z /= prior_z.sum()

            prior_chunk = pz.sum(dim=['ref_id', 'z'])
            prior_chunk = prior_chunk / prior_chunk.sum()

            pz = pz*(prior_z*prior_chunk)
            pz_norm = pz.sum(dim=['chunk', 'z'])
            pz = pz / pz_norm

        elif self.config['priors'] == 'test18':
            # Attempting chunk and z priors separately.
            from scipy.ndimage.filters import gaussian_filter

            prior_z = pz.sum(dim=['chunk', 'ref_id'])
            prior_z.values[:] = gaussian_filter(prior_z, self.config['nsmooth'])
            prior_z /= prior_z.sum()

            prior_chunk = pz.sum(dim=['ref_id', 'z'])
            prior_chunk = prior_chunk / prior_chunk.sum()

            pz = pz*(prior_z*prior_chunk)
            pz_norm = pz.sum(dim=['chunk', 'z'])
            pz = pz / pz_norm

            ipdb.set_trace()
        else:
            raise ValueError('Invalid prior type')
#            ipdb.set_trace()

        pz = pz.sum(dim='chunk')

        # Most of this should be moved into the libpzqual
        # library.
        pz = pz.rename({'ref_id': 'gal'})
        zb = libpzqual.zb(pz)
        odds = libpzqual.odds(pz, zb, self.config['odds_lim'])
        pz_width = libpzqual.pz_width(pz, zb, self.config['width_frac'])

        cat = pd.DataFrame()
        cat['zb'] = zb.values
        cat['odds'] = odds.values
        cat['pz_width'] = pz_width
        cat.index = pz.gal.values
        cat.index.name = 'ref_id'

        # Hack in test of a different quality parameter...
        chi2_min = chi2.min(dim=['chunk', 'z'])
        cat['qual_par'] = (chi2_min*pz_width).values

        odds0p2 = libpzqual.odds(pz, zb, self.config['odds_lim'])

        cat['Qz'] = (chi2_min*pz_width / odds0p2.values).values

#        ipdb.set_trace()

        return cat

    def run(self):
        # Ok, this is *bad*
        path = '/home/eriksen/tmp/p540/chi2_v1.h5'
        chi2 = xr.open_dataset(path).chi2

        self.output.result = self.entry(chi2)
