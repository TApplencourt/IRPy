#!/usr/bin/env python

'''
@author: T. Applencourt
'''

from setuptools import setup

setup(name="irpy",
      version=0.3,
      description = 'IRP for Python',
      long_description=read('README.md'),
      py_modules=['irpy'],
      author='Thomas Applencourt',
	  author_email='thomas.applencourt@irsamc.ups-tlse.fr',
	  url='https://github.com/TApplencourt/IRPy',
	  download_url = 'https://github.com/TApplencourt/IRPy/archive/master.tar.gz',
	  licence='WTFPL',
)
