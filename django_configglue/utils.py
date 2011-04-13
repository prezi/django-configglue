# Copyright 2010 Canonical Ltd.  This software is licensed under the
# GNU Lesser General Public License version 3 (see the file LICENSE).
import sys

from configglue.pyschema.parser import SchemaConfigParser


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
    for section, data in parser.values().items():
        for option, value in data.items():
            result[option.upper()] = encode(value)
    return result


def update_settings(parser, target):
    settings = get_django_settings(parser)
    settings.update({
        # keep parser reference
        '__CONFIGGLUE_PARSER__': parser,
        # save encoding used
        'SETTINGS_ENCODING': SETTINGS_ENCODING,
    })

    if isinstance(target, dict):
        # import config into target dict (for backwards compatibility)
        target.update(settings)
    else:
        # import config into target module
        if isinstance(target, basestring):
            # target is the module's name, so import the module first
            __import__(target)
            target = sys.modules[target]

        for name, value in settings.items():
            setattr(target, name, value)


def configglue(schema_class, configs, target):
    scp = SchemaConfigParser(schema_class())
    scp.read(configs)
    update_settings(scp, target)
    return scp
