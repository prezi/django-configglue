from optparse import make_option

from django.conf import settings, global_settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--global', action='store_true',
            dest='include_global',
            help='include global settings in lookup'),
        )
    help = """
    Read and write configuration options.

    command can be show, get or set
    """
    args = 'command [arg1 ...]'

    def handle(self, *args, **options):
        action = options.get('action')
        include_global = options.get('include_global')
        setting = options.get('setting')
        value = options.get('value')

        num_args = len(args)
        if action is None and num_args > 0:
            action = args[0]
        if setting is None and num_args > 1:
            setting = args[1].upper()
        if value is None and num_args > 2:
            value = args[2]

        if action == 'show':
            self.show(include_global)
        elif action == 'get':
            if setting is None:
                msg = 'GET command requires a setting name as argument'
                raise CommandError(msg)
            self.get(setting)
        elif action == 'set':
            if value is None:
                msg = 'SET command requires a setting name and a value ' \
                      'as arguments'
                raise CommandError(msg)
            self.set(setting, value)
        else:
            msg = "There is no such command: --%s" % action
            raise CommandError(msg)

    def show(self, include_global=False):
        global_settings_ = dir(global_settings)
        all_settings = (k for k in settings.get_all_members() \
                        if not (k.startswith('__') or k == 'get_all_members'))
        lines = []
        if include_global:
            local_settings = all_settings
        else:
            local_settings = (s for s in all_settings if s not in global_settings_)
        for name in local_settings:
            lines.append("%s = %s" % (name, repr(getattr(settings, name))))

        print '\n'.join(lines)

    def get(self, setting):
        marker = object()
        value = getattr(settings, setting, marker)
        if value is marker:
            print "Setting '%s' not found" % setting
        else:
            print "%s = %s" % (setting, value)

    def set(self, setting, value):
        old_value = getattr(settings, setting)
        setattr(settings, setting, value)
        print "%s = %s (was '%s')" % (setting, value, old_value)
