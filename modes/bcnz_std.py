# encoding: UTF8
from __future__ import print_function
import os
import pdb
import shutil
import numpy as np

import loadparts
import obj_hash
import bcnz_chi2
import bcnz_flux
import bcnz_norm
import bcnz_output

class standard:
    def __init__(self, conf, zdata, obs_file, out_name):

        self.conf = conf
        self.zdata = zdata
        self.obs_file = obs_file
        self.out_name = out_name

        self.conf['nmax'] = 10000

        obj_name = obj_hash.hash_structure(self.conf)

        root_dir = self.conf['root']
        self.cache_dir = os.path.join(root_dir, 'cache')
        self.obj_path = os.path.join(self.cache_dir, obj_name)


    def relink(self):
        """Link output file name to the object file."""

        if os.path.isfile(self.out_name):
            shutil.move(self.out_name, "%s.bak" % self.out_name)

        if os.path.islink(self.out_name):
            os.remove(self.out_name)

        os.symlink(self.obj_path, self.out_name)

    def run_file(self):
        if not os.path.isdir(self.cache_dir):
            os.mkdir(self.cache_dir)

        if self.conf['use_cache']:
            if os.path.isfile(self.obj_path):
                self.relink()
                return 

            self.estimate_photoz(self.obj_path)
            self.relink()
        else:
            self.estimate_photoz(self.out_name)


    def estimate_photoz(self, out_file):
        """Estimate the photoz for one input file."""

        obs_file = self.obs_file
        out_file = bcnz_output.output_file(out_file)

        if self.conf['get_z']:
            header = bcnz_output.create_header(self.conf, obs_file)
            header = ['{0}\n'.format(x) for x in header]
            out_file.writelines(header)

        nmax = self.conf['nmax']
        cols_keys, cols = bcnz_flux.get_cols(self.conf, self.zdata) 

#        pdb.set_trace()
        tmp = loadparts.loadparts(obs_file, nmax, cols_keys, cols)

        ndesi = self.conf['ndesi']
        columns = self.conf['order']+self.conf['others']
        rest = [('{%s:.%sf}' % (x, ndesi)) for x in columns]
        out_format = ' '.join(rest) + '\n'

        for data in tmp:
            data = bcnz_flux.post_pros(self.conf, data)
            #pdb.set_trace()
            f_obs, ef_obs = bcnz_flux.fix_fluxes(self.conf, self.zdata, data) 

            ids = data['ids']
            m_0 = data['m_0']
            z_s = data['z_s']
  
            f_obs, ef_obs = bcnz_norm.norm_data(self.conf, self.zdata, f_obs, ef_obs)

            inst = bcnz_chi2.chi2_inst(self.conf, self.zdata, f_obs, ef_obs, m_0, \
                          z_s, ids, 100)


            ng = len(f_obs)
            for block in inst.blocks():
                names = block.dtype.names
                in_dict = [dict(zip(names, record)) for record in block]

                lines = [out_format.format(**gal) for gal in in_dict]
                out_file.writelines(lines)
