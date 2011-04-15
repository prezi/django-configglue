# Copyright 2010 Canonical Ltd.  This software is licensed under the
# GNU Lesser General Public License version 3 (see the file LICENSE).

from setuptools import setup, find_packages

setup(
    # metadata
    name='django-configglue',
    version='0.4',
    author='Canonical ISD Hackers',
    author_email='canonical-isd@lists.launchpad.net',
    description='Django commands for managing configglue generated settings',
    long_description='Django commands for managing configglue generated '
        'settings from the command line.\n'
        'Commands are available to:\n'
        ' - get the value of a setting\n'
        ' - list all settings used (and their values)\n'
        ' - list all settings used, including django global settings (and\n'
        '   their values)\n'
        ' - locate the definition of a setting (useful when the configuration\n'
        '   is defined throughout several files)\n'
        ' - validate settings (make sure the values match the defined schema)',
    license='LGPLv3',
    keywords = ['django', 'configglue', 'configuration', 'settings'],
    url = 'https://launchpad.net/django-configglue/',
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Programming Language :: Python',
        'Topic :: Utilities',
    ],

    # content
    packages=find_packages(exclude=['testproject*']),
    install_requires=['django >= 1.0.2-final', 'configglue >= 0.9.1'],

    # tests
    test_suite='testproject.testrunner.runtests',
)
