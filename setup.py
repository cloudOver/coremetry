from distutils.core import setup
from setuptools import find_packages
from distutils.command.install import install as _install


setup(
  name = 'coremetry',
  packages = find_packages(exclude=['config']),
  version = '17.10.01',
  description = 'Monitoring suite for CoreCluster',
  author = 'Maciej Nabozny',
  author_email = 'maciej.nabozny@cloudover.io',
  url = 'http://cloudover.org/',
  download_url = 'https://github.com/cloudOver/coremetry/archive/master.zip',
  keywords = ['corecluster', 'cloudover', 'cloud', 'cloudinit'],
  classifiers = [],
  install_requires = ['corecluster'],
)
