# Copyright (C) 2013 Martin B. Eriksen
# This file is part of BCNz <https://github.com/PAU-survey/bcnz>.
#
# BCNz is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BCNz is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BCNz.  If not, see <http://www.gnu.org/licenses/>.
#!/usr/bin/env python
# encoding: UTF8

import glob
import pdb
from setuptools import setup, find_packages

# Same author and maintainer.
name = 'Martin B. Eriksen'
email = 'eriksen@pic.es'

setup(
    name = 'bcnz',
    version = '2',
    packages = find_packages(),

    install_requires = [
        'argparse',
        'astropy',
        'dask',
        'fire',
        'numpy',
        'matplotlib',
        'pandas',
        'pyarrow',
        'scipy',
        'sklearn',
        'psycopg2-binary',
        'tables',
        'tqdm',
        'xarray'
    ],
    author = name,
    author_email = email,
    license = 'GPLv3',
    maintainer = name,
    maintainer_email = email,
    scripts = ['bcnz/bin/run_bcnz.py'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Astronomy",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)"
    ],
)
