# Copyright 2010-2011 Canonical Ltd.
# Copyright Django Software Foundation and individual contributors
# This software is licensed under the
# GNU Lesser General Public License version 3 (see the file LICENSE)
# except where third-party/django/LICENSE applies.

from optparse import BadOptionError, OptionParser

import django
from django.core import management
from django.conf import settings

from configglue.glue import schemaconfigglue
from django_configglue import utils

_ = lambda s: s
# This hack is needed, because 1.8 got rid of LaxOptionParser
BaseOptionParser = getattr(management, 'LaxOptionParser', OptionParser)


class LaxOptionParser(BaseOptionParser):
    # Subclasses django's to avoid a bug

    def _process_long_opt(self, rargs, values):
        arg = rargs.pop(0)

        # Value explicitly attached to arg?  Pretend it's the next
        # argument.
        if "=" in arg:
            (opt, next_arg) = arg.split("=", 1)
            rargs.insert(0, next_arg)
            had_explicit_value = True
        else:
            opt = arg
            had_explicit_value = False

        try:
            opt = self._match_long_opt(opt)
        except BadOptionError:
            # Here's the addition in our subclass, we take care to take
            # the value back out of rargs so that it isn't duplicated if
            # this code path is hit.
            if had_explicit_value:
                rargs.pop(0)
            raise
        option = self._long_opt[opt]
        if option.takes_value():
            nargs = option.nargs
            if len(rargs) < nargs:
                if nargs == 1:
                    self.error(_("%s option requires an argument") % opt)
                else:
                    self.error(_("%s option requires %d arguments")
                               % (opt, nargs))
            elif nargs == 1:
                value = rargs.pop(0)
            else:
                value = tuple(rargs[0:nargs])
                del rargs[0:nargs]

        elif had_explicit_value:
            self.error(_("%s option does not take a value") % opt)

        else:
            value = None

        option.process(opt, value, values, self)


class GlueManagementUtility(management.ManagementUtility):
    def execute(self):
        """Override the base class to handle the schema-related options. """
        configglue_parser = getattr(settings, '__CONFIGGLUE_PARSER__', None)
        if configglue_parser is not None:
            # We need a lax option parser that:
            # - allows the '%prog subcommand [options] [args]' format
            # - will receive the schema options from configglue
            # - doesn't attempt to recognize django options
            lax_parser = LaxOptionParser(
                usage="%prog subcommand [options] [args]")
            parser, options, args = schemaconfigglue(
                configglue_parser, op=lax_parser, argv=self.argv)
            utils.update_settings(configglue_parser, settings)
            # remove schema-related options from the argv list
            self.argv = args
        super(GlueManagementUtility, self).execute()


def execute_from_command_line(argv=None):
    utility = GlueManagementUtility(argv)
    utility.execute()


if django.VERSION[:2] < (1, 4):
    # We're going to go ahead and use our own ManagementUtility here
    management.ManagementUtility = GlueManagementUtility
