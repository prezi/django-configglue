from setuptools import setup, find_packages

setup(
    name='django-schemaconfig',
    version='0.2',
    author='Canonical ISD Hackers',
    author_email='canonical-isd@lists.launchpad.net',
    license='Proprietary',
    packages=find_packages(),
    install_requires=['django >= 1.0.2-final', 'schemaconfig'],
)
