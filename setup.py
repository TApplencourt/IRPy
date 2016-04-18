#!/usr/bin/env python

import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name="irpy",
      version="0.4",
      description = 'IRP for Python',
      long_description=read('README.md'),
      packages=['irpy'],
      author='Thomas Applencourt',
	    author_email='thomas.applencourt@irsamc.ups-tlse.fr',
	    url='https://github.com/TApplencourt/IRPy',
	    download_url = 'https://github.com/TApplencourt/IRPy/archive/master.tar.gz',
	    license='WTFPL',
)
