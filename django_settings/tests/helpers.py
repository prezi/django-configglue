import os
import sys
from StringIO import StringIO

import django.conf
from django.core import management
from django.conf import settings
from django.test import TestCase


class CommandTestCase(TestCase):
    COMMAND = ''

    def begin_capture(self):
        self._stdout = sys.stdout
        self._stderr = sys.stderr
        sys.stdout = StringIO()
        sys.stderr = StringIO()

    def end_capture(self):
        sys.stdout.seek(0)
        sys.stderr.seek(0)

        self.capture = {'stdout': sys.stdout.read(),
                        'stderr': sys.stderr.read()}

        sys.stdout = self._stdout
        sys.stderr = self._stderr

    def call_command(self, *args, **kwargs):
        self.begin_capture()
        try:
            management.call_command(self.COMMAND, *args, **kwargs)
        finally:
            self.end_capture()


class SchemaConfigCommandTestCase(CommandTestCase):
    def setUp(self):
        super(SchemaConfigCommandTestCase, self).setUp()

        config = """
[django]
installed_apps = django_settings
"""
        self._DJANGO_SETTINGS_MODULE = self.set_config(config)

    def tearDown(self):
        self.load_settings(self._DJANGO_SETTINGS_MODULE)
        self.assertEqual(os.environ['DJANGO_SETTINGS_MODULE'],
                         self._DJANGO_SETTINGS_MODULE)

        os.remove('test.cfg')

        super(SchemaConfigCommandTestCase, self).tearDown()

    def set_config(self, config):
        config_file = open('test.cfg', 'w')
        config_file.write(config)
        config_file.close()

        return self.load_settings('test_django_settings.settings_schemaconfig')

    def load_settings(self, module):
        old_module = os.environ['DJANGO_SETTINGS_MODULE']
        # remove old settings module
        if old_module in sys.modules:
            del sys.modules[old_module]
        # force django to reload its settings
        settings._target = None
        # update settings module for next reload
        os.environ['DJANGO_SETTINGS_MODULE'] = module

        return old_module

