# Copyright 2010 Canonical Ltd.  This software is licensed under the
# GNU Lesser General Public License version 3 (see the file LICENSE).

import sys

import django
import django.core.management
from configglue.pyschema import schemaconfigglue
from django.core.management import ManagementUtility, LaxOptionParser
from django.core.management.base import BaseCommand
from django_configglue.utils import update_settings
from django.conf import settings


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
                                 option_list=BaseCommand.option_list,
                                 conflict_handler='resolve')
        configglue_parser = settings.__CONFIGGLUE_PARSER__
        op, options, args = schemaconfigglue(configglue_parser, op=parser,
                                             argv=self.argv)
        self.argv = args
        update_settings(configglue_parser, vars(settings))
        try:
            subcommand = self.argv[1]
        except IndexError:
            sys.stderr.write("Type '%s help' for usage.\n" % self.prog_name)
            sys.exit(1)

        if subcommand == 'help':
            if len(args) > 2:
                self.fetch_command(args[2]).print_help(self.prog_name, args[2])
            else:
                op.print_lax_help()
                sys.stderr.write(self.main_help_text() + '\n')
                sys.exit(1)
        # Special-cases: We want 'django-admin.py --version' and
        # 'django-admin.py --help' to work, for backwards compatibility.
        elif self.argv[1:] == ['--version']:
            # LaxOptionParser already takes care of printing the version.
            pass
        elif self.argv[1:] == ['--help']:
            op.print_lax_help()
            sys.stderr.write(self.main_help_text() + '\n')
        else:
            self.fetch_command(subcommand).run_from_argv(self.argv)

# We're going to go ahead and use our own ManagementUtility here, thank you.
django.core.management.ManagementUtility = GlueManagementUtility
