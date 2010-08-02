# Copyright 2010 Canonical Ltd.  This software is licensed under the
# GNU Lesser General Public License version 3 (see the file LICENSE).

from setuptools import setup, find_packages

setup(
    name='django-schemaconfig',
    version='0.2',
    author='Canonical ISD Hackers',
    author_email='canonical-isd@lists.launchpad.net',
    license='LGPLv3',
    packages=[x for x in find_packages() if not 'testproject' in x],
    install_requires=['django >= 1.0.2-final', 'schemaconfig'],
)
