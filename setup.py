from setuptools import setup
from Cython.Build import cythonize

setup(
    name="irpy",
    version="0.5.0",
    ext_modules = cythonize("irpy.pyx"),
    description = 'IRP for Python',
    long_description='Look a github README please.',
    url='https://github.com/TApplencourt/IRPy',
    download_url = 'https://github.com/TApplencourt/IRPy/archive/master.tar.gz',
    license='WTFPL',
    author='Thomas Applencourt',
    author_email='thomas.applencourt@irsamc.ups-tlse.fr',
)