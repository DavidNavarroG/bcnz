#!/usr/bin/env python
# encoding: UTF8

import copy
import pdb
import numpy as np
import time
from numpy.random import normal

import bcnz

def err_magnitude(conf, zdata, mag):
    """Error in magnitudes from the telescope and sky."""

    in_r = zdata['in_r']
    in_sky = zdata['in_sky']
    t_exp = zdata['t_exp']
    pix_size = conf['scale']**2.
    n_pix = conf['aperture'] / pix_size

    tel_surface = np.pi*(conf['D_tel']/2.)**2.
    pre = (tel_surface/n_pix)*(3631.0*1.51*1e7)

    # Filters are second index..
    yN_sig = pre*10**(-0.4*mag)*(in_r*t_exp)

    # For each filter..
    yN_sky = tel_surface*pix_size*(in_sky*t_exp)

    yStoN =  np.sqrt(n_pix*conf['n_exp'])*yN_sig / \
             np.sqrt(conf['RN']**2 + yN_sig + yN_sky)
    ynoise_ctn = 2.5*np.log10(1 + 0.02)
    yerr_m_obs = 2.5*np.log10(1.+ 1./yStoN)

    yerr_m_obs = np.sqrt(yerr_m_obs**2 + ynoise_ctn**2)

    return yerr_m_obs

def add_noise(conf, zdata, data):
    """Add noise in the magnitudes."""

    raise NotImplemented('Not updated with the latest changes..')

    # Note that the data is still in magnitudes even if the variable names
    # tell something else.. Yes, its confusing...

    mag = data['f_obs']
    zdata['t_exp'] = bcnz_exposure.texp(conf, zdata)
    err_mag = err_magnitude(conf, zdata, mag)

    ngal, nfilters = err_mag.shape
    add_mag = np.zeros((ngal, nfilters))
    for i in range(ngal):
        for j in range(nfilters):
            add_mag[i,j] += normal(scale=err_mag[i,j])

    to_use = err_mag < 0.5
    mag = data['f_obs']
    mag += to_use*add_mag
    data['f_obs'] = mag
    data['ef_obs'] = np.where(to_use, err_mag, -99.)


    return zdata