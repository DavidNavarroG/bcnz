#!/usr/bin/env python
# encoding: UTF8

# All the post processing after reading in the data.
import pdb
import numpy as np

import bcnz

def setid_m0s(conf, data):
    """Set ID and add magnitude zero points."""

    if 'id' in data:
        ids = data['id'].astype(np.int)
    else:
        ids = np.arange(data['mag'].shape[0])

    data['id'] = ids

    if 'm_0' in data:
        data['m_0'] += conf['delta_m_0']

    return data


def post_pros(conf, zdata, data):
    """Post processing of the observations."""

    data = setid_m0s(conf, data)

    if conf['add_noise']:
        bcnz.observ.noise.add_noise(conf, zdata, data)

    data = bcnz.observ.toflux(conf, zdata, data)
    return data