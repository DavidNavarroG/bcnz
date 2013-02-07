#!/usr/bin/env python
# encoding: UTF8

import copy

import standard
conf = copy.deepcopy(standard.conf)
conf['undet'] = 99
conf['zmax'] = 2.
conf['use_split'] = True
conf['catalog'] = "/Users/marberi/data/pau_mice/*.dat"
conf['use_cache'] = False
conf['use_par'] = False
