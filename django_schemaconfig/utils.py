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

def update_settings(parser, env):
    # import config into settings module
    settings = get_django_settings(parser)
    env.update(settings)
<<<<<<< TREE

# This function is based on code from the Django project.
# Please see the license file in the third-party/django directory
def execute_manager(settings, argv=None):
    parser = LaxOptionParser(usage="%prog subcommand [options] [args]",
                             version=get_version(),
                             option_list=BaseCommand.option_list)
    try:
        parser, options, args = schemaconfigglue(settings.parser, op=parser)
        update_settings(settings.parser, vars(settings))
        argv = [sys.argv[0]] + args
    except Exception:
        # capture errors to allow the manager to continue
        # they can be shown using django_settings'
        # settings --validate command
        argv = argv if argv is not None else sys.argv

    setup_environ(settings)
    utility = ManagementUtility(argv)
    utility.execute()
=======
>>>>>>> MERGE-SOURCE
