#!/usr/bin/env python
# encoding: UTF8

import copy
import ipdb
import numpy as np
import time
from numpy.random import normal
from scipy.interpolate import splev, splrep

import bcnz

def texp(conf, filters):
    """Find exposure time in each of the filters."""

    texpD = {}
    for f in ['up', 'g', 'r', 'i', 'z', 'y', 'Y', 'J', 'H', 'vis']:
        texpD[f] = conf['exp_{0}'.format(f)]


    for i, ftray in enumerate(conf['trays']):
        exp_time = conf['exp_t{0}'.format(i+1)]
        for f in ftray:
            texpD[f] = exp_time

    res = [texpD[x] for x in filters]

    return res

def err_mag(conf, zdata, mag):
    """Error in magnitudes from the telescope and sky."""

    in_r = zdata['in_r']
    in_sky = zdata['in_sky']
    t_exp = zdata['t_exp']
#    pix_size = conf['scale']**2.
#    n_pix = conf['aperture'] / pix_size

    all_filters = conf['filters']
    from_ground = np.array([(x not in conf['from_space']) for \
                            x in all_filters]) 

    t_exp = np.array(t_exp)
    dnoise = np.where(from_ground, conf['dnoise'], conf['dnoise_space'])
    n_pix = np.where(from_ground, conf['aperture'] / conf['pixscale']**2., \
                     conf['aperture'] / conf['pixscale_space']**2.)

#    ipdb.set_trace()
    N_rn = np.where(from_ground, conf['n_exp']*conf['RN']**2, \
                    conf['n_exp_space']*conf['RN_space']**2)


    N_dcur = n_pix*t_exp*dnoise

    D_tel = np.where(from_ground, conf['D_tel'], conf['D_tel_space'])
    tel_surface = np.pi*(D_tel/2.)**2.
    pre = (tel_surface/n_pix)*(3631.0*1.51*1e7)

#    ipdb.set_trace()

    # Filters are second index..
    n_exp = np.where(from_ground, conf['n_exp'], conf['n_exp_space'])
    N_sig = pre*n_exp*10**(-0.4*mag)*(in_r*t_exp)

    # For each filter..
    pix_size = np.where(from_ground, conf['pixscale']**2, conf['pixscale_space']**2.)
    N_sky = tel_surface*n_exp*pix_size*(in_sky*t_exp)
    N_sky = np.where(from_ground, N_sky, 0.)

#    SN =  np.sqrt(n_pix*conf['n_exp'])*N_sig / \
#          np.sqrt(N_rn + N_sig + N_dcur + N_sky)

    SN =  N_sig / np.sqrt(N_rn + N_sig + N_dcur + N_sky)

    # Adjusts the signal to noise to meet a specific criteria.
    if conf['use_snlim_space']:
        sn_val = conf['snlim_space']
        sn_mag = conf['snlim_space_mag']
        sn_ratio = np.ones(len(all_filters))
        for i,fname in enumerate(all_filters):
            if not fname in conf['from_space']:
                continue

            spl = splrep(mag[:,i], SN[:,i])
            sn_ratio[i] = sn_val / splev(sn_mag, spl)

        print('SN ratio', sn_ratio)
        SN = SN * sn_ratio


    err_m_obs = 2.5*np.log10(1.+ 1./SN)
    noise_ctn = 2.5*np.log10(1 + 0.02)

    err_m_obs = np.sqrt(err_m_obs**2 + noise_ctn**2)

    other = {'SN': SN, 'N_sig': N_sig, 'N_sky': N_sky,
             'N_rn': conf['RN']**2.}

    return err_m_obs, SN, other

def sn_spls(conf, zdata):
    """Construct splines with magnitude errors and SN."""

    import ipdb
    filters = zdata['filters']
    mag_interp = np.linspace(15., 35, 100)
    mag = np.tile(mag_interp, (len(filters), 1)).T


    merrD, sn_splD = {}, {}
    mag_err, SN, other = err_mag(conf, zdata, mag)
    for i,f in enumerate(filters):
        merrD[f] = splrep(mag_interp, mag_err[:,i])
        sn_splD[f] = splrep(mag_interp, SN[:,i])

#    ipdb.set_trace()

    return {'merrD': merrD, 'sn_splD': sn_splD}


def noise_info(conf, zdata):

    zdata['texp'] = texp(conf, zdata['filters'])
    zdata['sn_spls'] = sn_spls(conf, zdata)
 
    return noise_zdata

def OLDadd_noise(conf, zdata, data):
    """Add noise in the magnitudes."""

    raise NotImplentedError, 'This is moved...'

    zdata['t_exp'] = texp(conf, zdata['filters'])
    mag = data['mag']
    err_mag, SN = err_magnitude(conf, zdata, mag)

    ngal, nfilters = err_mag.shape
    add_mag = np.zeros((ngal, nfilters))
    for i in range(ngal):
        for j in range(nfilters):
            add_mag[i,j] += normal(scale=err_mag[i,j])

    to_use = np.logical_and(err_mag < 0.5, conf['sn_lim'] <= SN)

    mag += to_use*add_mag
    data['mag'] = mag
    data['emag'] = np.where(to_use, err_mag, -99.)


    return data
