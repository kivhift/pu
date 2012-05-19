import os
import sys
from distutils.core import setup

root_dir = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(root_dir, 'src'))
import pu

readme = open(os.path.join(root_dir, 'README'), 'r').read()

setup(
    name = 'pu',
    author = 'Joshua Hughes',
    author_email = 'kivhift@gmail.com',
    version = pu.__version__,
    url = 'http://github.com/kivhift/pu',
    license = 'MIT',
    package_dir = {'' : 'src'},
    packages = ['pu', 'pu.scons'],
    description = 'Python utilities',
    long_description = readme,
    classifiers = [
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python'
    ]
)
