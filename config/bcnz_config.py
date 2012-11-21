#!/usr/bin/env python
# encoding: UTF8

import numpy as np

conf = {

    'pr_a': [2.369,1.843,1.843,1.340,1.340,1.340],
    'pr_zo': [0.387,0.390,0.390,0.208,0.208,0.208],
    'pr_km': [0.119,0.093,0.093,0.130,0.130,0.130],
    'pr_fo_t': [0.48,0.22,0.22],

    'pr_k_t': [0.186,0.038,0.038],


    'use_cache': False,
    'tblock': True,
    'dz_bright': 0.001,
    'dz_faint': 0.005,
    'min_rms_bright': 0.0055,
    'min_rms_faint': 0.055,
    'mag_split': 22.5,
    'use_split': False,
    'opt': True,
    'others': [],
    'order': ['id', 'zb', 'zb_min', 'zb_max', 't_b', 'odds', 'z_ml', 't_ml', 'chi2', 'm_0', 'z_s'],
    'm_step': 0.1,
    'output': '',
    # Telescope noise parameters.
    'D_tel': 4.2,
    'aperture': 2.0,
    'scale': 0.27,
    'n_exp': 2.,
    'RN': 5.,

    'trays': 'tray_matrix_42NB.txt',
    'exp_trays': [45,45,45,50,60,70],
    'vign': [1.,0.75, 0.375],
    'sky_spec': 'sky_spectrum.txt',

    'add_noise': False,
    'old_model': False,
    'ab_tmp': 'ab',
    'zmax_ab': 12.,
    'dz_ab': 0.01,
    'prior': 'pau',
    'train': False,
    'norm_flux': False,
    'ab_dir': 'AB',
    'filter_dir': 'FILTER',
    'sed_dir': 'SED',
    'p_min': 0.01,
    'merge_peaks': False,
    'interactive': False,
    'plots': False,
    'probs_lite': True,
    'mag': True,
    'spectra': 'spectras.txt',
    'get_z': True,
    'use_par': True,
    'nthr': None,
    'columns': 'mock.columns',
    'add_spec_prob': False,
    'zc': False,
    'nmax': False,
    'probs': False,
    'probs2': False,
    'convolve_p': False,
    'photo_errors': True,
    'z_thr': 0.,
    'color': False,
    'zp_offsets': 0.,
    'ntypes': [],
    'madau': False,
    'new_ab': False,
    'exclude': [],
    'zmin': 0.01,
    'zmax': 10.,
    'unobs': -99.,
    'undet': 99.,
    'delta_m_0': 0.,
    'n_peaks': 1,
    'verbose': True,
    'min_magerr': 0.001,
    'catalog': None,
    'interp': 2,
    'prior': 'pau',
    'dz': 0.01,
#    'odds': 0.95,
    'odds': 0.68,
    'min_rms': 0.05}
