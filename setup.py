#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from __future__ import absolute_import, print_function

from glob import glob
from os.path import abspath, basename, dirname, join, splitext

from setuptools import find_packages, setup

here = abspath(dirname(__file__))

requirements = []
keywords_list = []

__title__ = 'eink_explorations'
__description__ = 'eink_explorations by Victor Leung'
__url__ = 'https://github.com/yck011522/eink_explorations'
__version__ = '0.1.0'
__author__ = 'Victor Leung'
__author_email__ = 'yck011522@gmail.com'
__license__ = 'MIT license'
__copyright__ = 'Copyright 2021'


setup(
    name="",
    version=__version__,
    license=__license__,
    description=__description__,
    author=__author__,
    author_email=__author_email__,
    url=__url__,
    long_description='Library for designing timber structures with integral joints.',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Scientific/Engineering',
    ],
    keywords=keywords_list,
    install_requires=requirements,
    extras_require={},
    entry_points={},
)
