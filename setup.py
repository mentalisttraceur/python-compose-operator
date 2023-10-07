#!/usr/bin/env python

import errno
import os
import sys

from setuptools import setup

from compose_operator import __doc__, __version__

project_directory = os.path.abspath(os.path.dirname(__file__))
readme_path = os.path.join(project_directory, 'README.rst')

readme_file = open(readme_path)
try:
    long_description = readme_file.read()
finally:
    readme_file.close()

setup(
    name='compose-operator',
    version=__version__,
    description=__doc__.split('\n')[0],
    long_description=long_description,
    license='0BSD',
    url='https://github.com/mentalisttraceur/python-compose-operator',
    author='Alexander Kozhevnikov',
    author_email='mentalisttraceur@gmail.com',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    py_modules=['compose_operator'],
    python_requires=">=3.8",
    requires=[
        'compose (>=1.4.8)',
        'wrapt (>=1.15.0)',
    ],
)
