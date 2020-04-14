#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os import path
from setuptools import setup
import importlib

dependencies = [ 'QtPy>=1.7.0' ]

for binding in ['PySide2', 'PyQt5', 'PySide', 'PyQt']:
	spec = importlib.util.find_spec(binding)
	if spec is not None:
		break
else:
	dependencies.append('PySide2>=5.12.2')


this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
	long_description = f.read()

setup(
	name='argparseqt',
	version='0.3.1',
	description='An easy way to make Qt GUIs using the argparse standard module',
	url='https://github.com/domstoppable/argparseqt',
	author='Dominic Canare',
	author_email='dom@dominiccanare.com',
	license='MIT',
	packages=['argparseqt'],
	install_requires=dependencies,
	long_description=long_description,
	long_description_content_type='text/markdown'
)
