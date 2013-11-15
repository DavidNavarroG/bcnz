#!/usr/bin/env python
# encoding: UTF8

# Runs multiple catalog files in parallel. In the future it might
# be replaced by another framework.

import glob
import os
import pdb
import multiprocessing
import types

import bcnz
import bcnz.io
import bcnz.model
import bcnz.zdata

import pzcat

import bcnz.lib.obj_hash

class local_task(pzcat.pzcat):
    def __init__(self, myconf, zdata, in_iter, out_table):
        self.config = bcnz.libconf(myconf)
        self.zdata = zdata
        self.in_iter = in_iter
        self.out_table = out_table 

#        self.conf = config

    def run(self):
        print('Running photoz')
        self._run_iter(self.in_iter, self.out_table)

def prepare_tasks(config, zdata):
    """Objects encapsulating the runs."""

    cat_files = glob.glob(config['cat'])
    msg_noinput = 'Found no input files for: {0}'.format(config['cat'])

    assert not (1 < len('cat_files') and \
                isinstance(config['output'], types.NoneType))

    if config['output']:
        obs_file = cat_files[0]
        ans = [bcnz_std.standard(config, zdata, obs_file, config['output'])]
        return ans

    in_fmt = config['in_format']
    out_fmt = config['out_format']

    tasks = []
    for obs_file in cat_files:
        out_file = '%s.bcnz' % os.path.splitext(obs_file)[0]

        in_iter = getattr(bcnz.io, in_fmt).read_cat(config, zdata, obs_file)
        out_table = getattr(bcnz.io, out_fmt).write_cat(config, out_file)

        tasks.append(local_task(config, zdata, in_iter, out_table))

    return tasks

def run(task):
    """The pool.map require a function. Defining a closure inside
       run_tasks or using lambda fails badly.
    """

    task.run()

def run_tasks(config, zdata, tasks):
    """Execute either using multiprocessing or just run tasks in serial."""

    use_par = config['use_par'] and 1 < len(tasks)
    if use_par:
        nthr = config['nthr']
        ncpu = multiprocessing.cpu_count()
        nparts = nthr if nthr else ncpu
        #pdb.set_trace()
        pool = multiprocessing.Pool(processes=nparts)
        pool.map(run, tasks)
    else:
        for task in tasks:
            task.run()

class pzcat_local(object):
    def __init__(self, myconf):
        self.config = bcnz.libconf(myconf)

        # My code needs this convention..
        self.conf = self.config

    @property
    def hashid(self):
        return bcnz.lib.obj_hash.hash_structure(self.conf)

    def run(self):
        print('herX')

        # Estimate the photoz
        zdata = bcnz.zdata.zdata(self.config)
        zdata = bcnz.model.add_model(self.config, zdata)

        tasks = prepare_tasks(self.config, zdata)
        run_tasks(self.config, zdata, tasks)
