#This file mainly exists to allow python setup.py test to work.
import os
import sys


def runtests():
    curdir = os.getcwd()
    testproject = os.path.join(curdir, 'testproject')
    os.chdir(testproject)
    sys.path.append(curdir)

    os.environ['DJANGO_SETTINGS_MODULE'] = 'testproject.settings'

    from django.core.management import call_command

    call_command('test', 'django_configglue')
    sys.exit(0)

