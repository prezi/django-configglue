import sys

from django import get_version
from django.core.management import (LaxOptionParser, setup_environ,
    ManagementUtility)
from django.core.management.base import BaseCommand
from schemaconfig import schemaconfigglue


SETTINGS_ENCODING = 'utf-8'


def get_django_settings(parser):
    def encode(item):
        if isinstance(item, basestring):
            value = item.encode(SETTINGS_ENCODING)
        elif isinstance(item, dict):
            items = encode(item.items())
            value = dict(items)
        elif isinstance(item, (list, tuple)):
            value = map(encode, item)
        else:
            value = item
        return value

    result = {}
    for k, v in parser:
        result[k.upper()] = encode(v)
    return result

def update_settings(parser, env):
    # import config into settings module
    settings = get_django_settings(parser)
    env.update(settings)

def execute_manager(settings, argv=None):
    parser = LaxOptionParser(usage="%prog subcommand [options] [args]",
                             version=get_version(),
                             option_list=BaseCommand.option_list)
    try:
        parser, options, args = schemaconfigglue(settings.parser, op=parser)
        update_settings(settings.parser, vars(settings))
        argv = [sys.argv[0]] + args
    except Exception, e:
        # capture errors to allow the manager to continue
        # they can be shown using django_settings'
        # settings --validate command
        argv = argv if argv is not None else sys.argv

    setup_environ(settings)
    utility = ManagementUtility(argv)
    utility.execute()
