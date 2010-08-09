# Copyright 2010 Canonical Ltd.  This software is licensed under the
# GNU Lesser General Public License version 3 (see the file LICENSE).

from setuptools import setup, find_packages

setup(
    name='django-configglue',
    version='0.2',
    author='Canonical ISD Hackers',
    author_email='canonical-isd@lists.launchpad.net',
    license='LGPLv3',
    packages=find_packages(exclude=['testproject*']),
    install_requires=['django >= 1.0.2-final', 'configglue'],
)
