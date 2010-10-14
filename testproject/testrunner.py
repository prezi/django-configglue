#This file mainly exists to allow python setup.py test to work.
import os
import sys


def runtests():
    curdir = os.getcwd()
    testproject = os.path.join(curdir, 'testproject')
    os.chdir(testproject)
    sys.path.append(curdir)

    os.environ['DJANGO_SETTINGS_MODULE'] = 'testproject.settings'

    from django.conf import settings
    from django.test.utils import get_runner

    test_runner = get_runner(settings)
    failures = test_runner(['django_configglue'], verbosity=1, interactive=True)
    sys.exit(failures)

