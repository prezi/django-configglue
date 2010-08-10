# Copyright 2010 Canonical Ltd.  This software is licensed under the
# GNU Lesser General Public License version 3 (see the file LICENSE).

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
    # import config into settings module
    settings = get_django_settings(parser)
    if isinstance(target, dict):
        target.update(settings)
    else:
        for name, value in settings.items():
            setattr(target, name, value)
