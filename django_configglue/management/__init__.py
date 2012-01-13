# Copyright 2010-2011 Canonical Ltd.
# Copyright Django Software Foundation and individual contributors
# This software is licensed under the
# GNU Lesser General Public License version 3 (see the file LICENSE)
# except where third-party/django/LICENSE applies.


from optparse import BadOptionError
import sys

import django
import django.core.management
from configglue.glue import schemaconfigglue
from django.core.management import ManagementUtility, LaxOptionParser as _LaxOptionParser
from django.core.management.base import BaseCommand, handle_default_options
from django.conf import settings
from django_configglue import utils


class LaxOptionParser(_LaxOptionParser):
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


class GlueManagementUtility(ManagementUtility):
    # This function was mostly taken from the django project.
    # Please see the license file in the third-party/django directory.
    def execute(self):
        """
        Given the command-line arguments, this figures out which subcommand is
        being run, creates a parser appropriate to that command, and runs it.
        """
        # Preprocess options to extract --settings and --pythonpath.
        # These options could affect the commands that are available, so they
        # must be processed early.
        parser = LaxOptionParser(usage="%prog subcommand [options] [args]",
                                 version=django.get_version(),
                                 option_list=BaseCommand.option_list)
        try:
            configglue_parser = settings.__CONFIGGLUE_PARSER__
            parser, options, args = schemaconfigglue(configglue_parser,
                op=parser, argv=self.argv)
            # remove schema-related options from the argv list
            self.argv = args
            utils.update_settings(configglue_parser, settings)
        except AttributeError:
            # no __CONFIGGLUE_PARSER__ found, fall back to standard django
            # options parsing
            options, args = parser.parse_args(self.argv)
            handle_default_options(options)
        except:
            # Ignore any option errors at this point.
            args = self.argv

        try:
            subcommand = self.argv[1]
        except IndexError:
            sys.stderr.write("Type '%s help' for usage.\n" % self.prog_name)
            sys.exit(1)

        if subcommand == 'help':
            if len(args) > 2:
                self.fetch_command(args[2]).print_help(self.prog_name, args[2])
            else:
                parser.print_lax_help()
                sys.stderr.write(self.main_help_text() + '\n')
                sys.exit(1)
        # Special-cases: We want 'django-admin.py --version' and
        # 'django-admin.py --help' to work, for backwards compatibility.
        elif self.argv[1:] == ['--version']:
            # LaxOptionParser already takes care of printing the version.
            pass
        elif self.argv[1:] == ['--help']:
            parser.print_lax_help()
            sys.stderr.write(self.main_help_text() + '\n')
        else:
            self.fetch_command(subcommand).run_from_argv(self.argv)


# We're going to go ahead and use our own ManagementUtility here, thank you.
django.core.management.ManagementUtility = GlueManagementUtility
