import sys
from optparse import make_option

from django.conf import settings, global_settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--global', action='store_true',
            dest='include_global',
            help='include global settings in lookup'),
        make_option('--show', action='store_true', dest='show_current',
            help='show current settings'),
        )
    help = 'Show settings'
    args = '[setting ...]'

    def handle(self, *args, **options):
        show_current = options.get('show_current')
        include_global = options.get('include_global')

        if not args and not show_current:
            self.print_help(sys.argv[0], sys.argv[1])
            return

        if args:
            settings = map(str.upper, args)
            self.get(settings)

        if show_current:
            self.show(include_global)

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
            lines.append("%s = %r" % (name, getattr(settings, name)))

        print '\n'.join(lines)

    def get(self, keys):
        __marker = object()
        for key in keys:
            value = getattr(settings, key, __marker)
            if value is __marker:
                print "setting '%s' not found" % key
            else:
                print "%s = %r" % (key, value)

