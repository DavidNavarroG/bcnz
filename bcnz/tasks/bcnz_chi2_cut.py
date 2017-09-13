#!/usr/bin/env python

from __future__ import print_function

import ipdb
import os
import time
import numpy as np
import pandas as pd
import xarray as xr
import itertools as it

from scipy.interpolate import splrep, splev, splint
from scipy.integrate import trapz, simps

from matplotlib import pyplot as plt
import xdolphin as xd

descr = {
  'filters': 'Filters to use',
  'seds': 'SEDs to use',
#  'zmin': 'Minimum redshift',
#  'zmax': 'Maximum redshift',
#  'dz': 'Grid width in redshift',
  'chi2_algo': 'The chi2 algorithm',
#  'use_lines': 'If including emission lines',
#  'use_ext': 'If including extinction'
  'max_chi2': 'Maximal chi2 value'
}

class bcnz_chi2_cut:
    """Fitting a linear combination to the observations."""

    # Experimenting with removing the worst chi^2 outliers..

    # Some of these configuration options are no longer valid and 
    # moved into the flux_model code...
    version = 1.061
    config = {
      'filters': [],
      'seds': [],
      'zmin': 0.01,
      'zmax': 2.0,
      'dz': 0.01,
      'odds_lim': 0.01,
      'Niter': 200,
      'line_weight': 2.,
      'chi2_algo': 'min',
      'use_lines': True,
      'use_ext': False,
      'max_chi2': 100.
    }

    def check_conf(self):
        assert self.config['filters'], 'Need to set filters'
        assert self.config['seds'], 'Need to set: seds'


    def get_arrays(self, data_df):
        """Read in the arrays and present them as xarrays."""

        # Seperating this book keeping also makes it simpler to write
        # up different algorithms.
        filters = self.config['filters']
        dims = ('gal', 'band')
        flux = xr.DataArray(data_df['flux'][filters], dims=dims)
        flux_err = xr.DataArray(data_df['flux_err'][filters], dims=dims)

        # Not exacly the best, but Numpy had problems with the fancy
        # indexing.
        to_use = ~np.isnan(flux_err)

        # This gave problems in cases where all measurements was removed..
        flux.values = np.where(to_use, flux.values, 1e-100) #0.) 

        var_inv = 1./(flux_err + 1e-100)**2
        var_inv.values = np.where(to_use, var_inv, 1e-100)
        flux_err.values = np.where(to_use, flux_err, 1e-100)


        return flux, flux_err, var_inv

    def normal_chi2(self, ab, data_df):
        """chi2 estimation."""

        flux, flux_err, var_inv = self.get_arrays(data_df)

        f_mod = self.model(ab)
        S = (var_inv*flux**2).sum(dim='f')
        X = (var_inv*flux).dot(f_mod)
        M = var_inv.dot(f_mod**2)

        chi2 = S - X**2 / M
        norm = X / M

        return chi2, norm

    def chi2_min(self, f_mod, data_df, zs): #, mabs_df):
        """Minimize the chi2 expression."""

        flux, flux_err, var_inv = self.get_arrays(data_df)

        t1 = time.time()
#        A = np.einsum('gf,zsf,ztf->gzst', var_inv, f_mod, f_mod)
        A = np.einsum('gf,zfs,zft->gzst', var_inv, f_mod, f_mod)

        # Bad hack..
#        A = np.clip(A, 1e-50, np.infty)
        print('time A',  time.time() - t1)

        t1 = time.time()
#        b = np.einsum('gf,gf,zsf->gzs', var_inv, flux, f_mod)
        b = np.einsum('gf,gf,zfs->gzs', var_inv, flux, f_mod)
        print('time b',  time.time() - t1)

        Ap = np.where(A > 0, A, 0)
        An = np.where(A < 0, -A, 0)

        v = 100*np.ones_like(b)

        gal_id = np.array(data_df.index)
        coords = {'gal': gal_id, 'band': f_mod.band, 'z': f_mod.z}
        coords_norm = {'gal': gal_id, 'z': f_mod.z, 'model': f_mod.model}


        t1 = time.time()
        for i in range(self.config['Niter']):
            a = np.einsum('gzst,gzt->gzs', Ap, v)

            if (a==0).any():
                ipdb.set_trace()

            m0 = b / a
            vn = m0*v

            # Comparing with chi2 would require evaluating this in each
            # iteration..
            adiff = np.abs(vn-v)

            v = vn

        print('time minimize',  time.time() - t1)
        # .. Also changed in last update of einsum
        F = np.einsum('zfs,gzs->gzf', f_mod, v)
        F = xr.DataArray(F, coords=coords, dims=('gal', 'z', 'band'))

        chi2_band = var_inv*(flux - F)**2
        chi2_band = np.clip(chi2_band, 0., self.config['max_chi2'])
        max_chi2 = self.config['max_chi2']

        # Another test...
        chi2_band.values = np.where(chi2_band < 5., chi2_band, 0.)

        pb = np.exp(-0.5*chi2_band.sum(dim='band'))
        pb = pb / (1e-100 + pb.sum(dim='z'))
        chi2 = chi2_band.sum(dim='band')

        norm = xr.DataArray(v, coords=coords_norm, dims=('gal','z','model'))

        return chi2, norm, chi2_band

    def best_model(self, norm, f_mod, peaks):
        """Estimate the best fit model."""

        # Moving this elsewhere is not as easy as it seems. The amplitude data
        # is huge and creates problems.
        L = [] 

        fluxA = np.zeros((len(peaks), len(f_mod.band)))
        for i,gal in enumerate(peaks.index):
            zgal = peaks.loc[gal].zb
            norm_gal = norm.sel(gal=gal, z=zgal).values
            fmod_gal = f_mod.sel(z=zgal).values

            fluxA[i] = np.dot(fmod_gal, norm_gal)

        coords = {'gal': norm.gal, 'band': f_mod.band}
        flux = xr.DataArray(fluxA, dims=('gal', 'band'), coords=coords)

        return flux


    def odds_fast(self, pz, zb):

        # Very manual determination of the ODDS through the
        # cumsum function. xarray is n version 0.9.5 not
        # supporting integration.
        odds_lim = self.config['odds_lim']
        z1 = zb - odds_lim*(1.+zb)
        z2 = zb + odds_lim*(1.+zb)

        # When the galaxy is close to the end of the grid.
        z = pz.z.values
        z1 = np.clip(z1, z[0], z[-1])
        z2 = np.clip(z2, z[0], z[-1])


        # This assumes a regular grid.
        dz = self.config['dz']
        z0 = z[0]
        bins1 = (z1 - z0) / dz - 1 # Cumsum is estimated at the end
        bins2 = (z2 - z0) / dz - 1
        i1 = np.clip(np.floor(bins1), 0, np.infty).astype(np.int)
        i2 = np.clip(np.floor(bins2), 0, np.infty).astype(np.int)
        db1 = bins1 - i1
        db2 = bins2 - i2

        # Here the cdf is estimated using linear interpolation
        # between the points. This is done because the cdf is
        # changing rapidly for a large sample of galaxies.
        cumsum = pz.cumsum(dim='z')
        E = np.arange(len(pz))

        def C(zbins):
            return cumsum.isel_points(gal=E, z=zbins).values

        cdf1 = db1*C(i1+1) + (1.-db1)*C(i1)
        cdf2 = db2*C(i2+1) + (1.-db2)*C(i2)
        odds = cdf2 - cdf1

        # This version is similar to BPZ / BCNzv1
        old_odds = C(i2+1) - C(i1)

        return old_odds, odds

    def photoz(self, chi2, norm):
        pzcat = pd.DataFrame(index=chi2.gal)

        has_sed = 'sed' in chi2.dims
        dims = ['sed', 'z'] if has_sed else ['z']
        delta_chi2 = chi2 - chi2.min(dim=dims)
        pzt = np.exp(-0.5*delta_chi2)

        pz = pzt.sum('sed') if has_sed else pzt
        pz = pz / pz.sum(dim='z')

        izmin = pz.argmax(dim='z')
        zb = pz.z[izmin]
        pzcat['zb'] = zb

        old_odds, odds = self.odds_fast(pz, zb)
        pzcat['odds_old'] = old_odds
        pzcat['odds'] = odds

        # Ok, this should be written better...
        L = []
        for i,iz in enumerate(izmin):
            L.append(norm.values[i,iz].argmax())

        pzcat['tmax'] = np.array(L)
        pzcat['chi2'] = np.array(chi2.min(dim=dims))

        return pzcat, pz

    def fix_fmod_format(self, fmod_in):
        f_mod = fmod_in.to_xarray().f_mod
        f_mod = f_mod.stack(model=['sed', 'EBV'])

        return f_mod
#        ipdb.set_trace()

    def run(self):
        self.check_conf()

        algo = self.config['chi2_algo']
        key = 'chi2_{}'.format(algo)
        assert hasattr(self, key), 'No such key: {}'.format(key)
        f_algo = getattr(self, key)

        galcat = self.job.galcat.result
        f_mod = self.fix_fmod_format(self.job.f_mod.result)

        galcat_store = self.job.galcat.get_store()
        chunksize = 10
        Rin = galcat_store.select('default', iterator=True, chunksize=chunksize)

        zs = False
#        zs = self.job.zspec.result.zs

        path = self.job.empty_file('default')
        store = pd.HDFStore(path)
        for i,galcat in enumerate(Rin):
            print('batch', i, 'tot', i*chunksize)

            chi2, norm,chi2_band = f_algo(f_mod, galcat, zs)
            peaks,pz = self.photoz(chi2, norm)
            best_model = self.best_model(norm, f_mod, peaks)

            # Required by xarray..
            norm.name = 'norm'
            chi2_band.name = 'chi2'
            pz.name = 'pz'
            best_model.name = 'best_model'

            # Storing with multiindex will give problems.
            norm = norm.unstack(dim='model')

            # This should be configurable somewhere. It takes a lot of storage..
            store.append('default', peaks.stack()) 
            store.append('norm', norm.to_dataframe())
            store.append('pz', pz.to_dataframe())
            store.append('best_model', best_model.to_dataframe())

            store.append('chi2', chi2_band.to_dataframe()) 

        store.close()
