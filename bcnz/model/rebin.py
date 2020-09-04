#!/usr/bin/env python
# encoding: UTF8

from IPython.core import debugger as ipdb
import time
import numpy as np
import pandas as pd
from scipy.interpolate import splrep, splev, splint

descr = {
  'zmin': 'Minimum redshift',
  'zmax': 'Maximum redshift',
  'dz': 'Grid width in redshift'
}

def_config = {'zmin': 0.01, 'zmax': 1.2, 'dz': 0.001}

def rebin(model, **myconf):
    """Rebinning the redshift grid of the model."""

    config = def_config.copy()
    config.update(myconf)

    C = config
    zgrid = np.arange(C['zmin'], C['zmax']+C['dz'], C['dz'])

    inds = ['band', 'sed', 'ext_law', 'EBV']
    model = model.reset_index().set_index(inds)

    print('starting to rebin')
    t1 = time.time()
    rebinned = pd.DataFrame()
    for key in model.index.unique():
        sub = model.loc[key]
        spl = splrep(sub.z, sub.flux)

        # Just since it failed once..
        try:
            part = pd.DataFrame({'z': zgrid, 'flux': splev(zgrid, spl, ext=2)})
        except ValueError:
            ipdb.set_trace()

        # I needed to set these manually...
        for k1, v1 in zip(model.index.names, key):
            part[k1] = v1

        rebinned = rebinned.append(part)

    print('time', time.time() - t1)
    rebinned = rebinned.reset_index().set_index(inds+['z'])

    return rebinned