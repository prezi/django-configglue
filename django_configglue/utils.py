# Copyright 2010-2011 Canonical Ltd.  This software is licensed under the
# GNU Lesser General Public License version 3 (see the file LICENSE).
import imp
import os
import sys

from configglue.parser import SchemaConfigParser


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


def get_project_settings():
    """ Find project_template settings file, in 1.4 you can't just use import """
    from django import conf

    project_template_dir = os.path.join(
        os.path.dirname(conf.__file__),
        'project_template')
    for root, dirs, files in os.walk(project_template_dir):
        if 'settings.py' in files:
            return imp.load_source('project_settings',
                                   os.path.join(root, 'settings.py'))
