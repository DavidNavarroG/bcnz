#!/usr/bin/env python
# encoding: UTF8

import pdb
import bcnz
import bcnz.config

import bcnz.priors
import bcnz.lib
import bcnz.modes

class pzcat:
    def __init__(self, myconf):
        # I should write a better config object...
        conf = bcnz.config.bright.conf.copy() # HACK 
        conf['obs_files'] = ['photoz/mock_bright.cat']
        conf.update(myconf)

        self.conf = conf

    def calc(self):
        zdata = bcnz.lib.bcnz_zdata.find_zdata(self.conf)
        zdata = bcnz.lib.bcnz_filters.filter_and_so()(self.conf, zdata)
        bcnz.modes.bcnz_main.wrapper(self.conf, zdata)

        pdb.set_trace()

    def load(self, file_path):
        pdb.set_trace()
