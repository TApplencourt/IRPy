from distutils.core import setup
from distutils.extension import Extension

try:
    from Cython.Build import cythonize
except ImportError:
    USE_CYTHON = False
else:
    USE_CYTHON = True

ext = '.pyx' if USE_CYTHON else '.c'
extensions = [Extension("example", ["example"+ext])]

if USE_CYTHON:
    extensions = cythonize(extensions)

setup(
    name="irpy",
    version="0.5.0",
    ext_modules = extensions,
    description = 'IRP for Python',
    long_description='Look a github README please.',
    url='https://github.com/TApplencourt/IRPy',
    download_url = 'https://github.com/TApplencourt/IRPy/archive/master.tar.gz',
    license='WTFPL',
    author='Thomas Applencourt',
    author_email='thomas.applencourt@irsamc.ups-tlse.fr',
)