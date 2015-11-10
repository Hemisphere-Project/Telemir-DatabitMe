# -*- coding: utf-8 -*-

from setuptools import setup
import os

long_description = open("README.rst").read()

setup(
    name = "TeleMir",
    version = '0.1.0dev',
    packages = ['TeleMir', ],
    install_requires=[
                    'numpy',
                    'pyzmq',
                    'pyacq',
                    'pyqtgraph',
                    ],
    author = "A.Corneyllie",
    author_email = "alexandra.corneyllie@gmail.com",
    description = "Pure Python EEG acquisition and trasformation to cognitive ship performance.",
    long_description = long_description,
    license = "BSD",
    url='http://neuralensemble.org/neo',
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering']
)
