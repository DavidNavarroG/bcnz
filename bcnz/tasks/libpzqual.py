#!/usr/bin/env python
# encoding: UTF8

# Library containing the methods for estimating photo-z quality
# paramters.

def odds(pz, zb, odds_lim):
    """ODDS quality paramter."""

    # Very manual determination of the ODDS through the
    # cumsum function. xarray is n version 0.9.5 not
    # supporting integration.
    z1 = zb - odds_lim*(1.+zb)
    z2 = zb + odds_lim*(1.+zb)

    # When the galaxy is close to the end of the grid.
    z = pz.z.values
    z1 = np.clip(z1, z[0], z[-1])
    z2 = np.clip(z2, z[0], z[-1])

    # This assumes a regular grid.
    z0 = z[0]
    dz = float(z[1] - z[0])
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

    return odds

def pz_width(pz, zb):
    """Estimate the pz_width quality parameter."""

    # The redshift width with a fraction frac (see below) of the pdf on
    # either side. The ODDS require a different ODDS limit for different
    # magnitudes and fractions to be optimal, while this quality parameter
    # is more robust. The estimation use the first derivative of the
    # cumsum to estimate pz_width, since a discrete pz_width is problematic
    # when cutting.

    frac = 0.01
    cumsum = pz.cumsum(dim='z')
    ind1 = (cumsum > frac).argmax(axis=1) - 1
    ind2 = (cumsum > 1-frac).argmax(axis=1) -1

    igal = range(len(cumsum))
    y1_a = cumsum.isel_points(z=ind1, gal=igal)
    dy1 = (cumsum.isel_points(z=ind1+1, gal=igal) - y1_a) / \
          (cumsum.z[ind1+1].values - cumsum.z[ind1].values)

    y2_a = cumsum.isel_points(z=ind2, gal=igal)
    dy2 = (cumsum.isel_points(z=ind2+1, gal=igal) - y2_a) / \
          (cumsum.z[ind2+1].values - cumsum.z[ind2].values)

    dz1 = (frac - y1_a) / dy1
    dz2 = ((1-frac) - y2_a) / dy2
    pz_width = 0.5*(cumsum.z[(cumsum > 1-frac).argmax(axis=1)].values \
                    + dz2.values \
                    - cumsum.z[(cumsum > frac).argmax(axis=1)].values \
                    - dz1.values)

    return pz_width