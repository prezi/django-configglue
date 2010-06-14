import os
import sys
from StringIO import StringIO

import django.conf
from django.core import management
from django.conf import settings
from django.test import TestCase


class DjangoCommandTestCase(TestCase):
    COMMAND = ''

    def setUp(self, module='test_django_settings.settings'):
        self._DJANGO_SETTINGS_MODULE = self.load_settings(module)

    def tearDown(self):
        self.load_settings(self._DJANGO_SETTINGS_MODULE)
        self.assertEqual(os.environ['DJANGO_SETTINGS_MODULE'],
                         self._DJANGO_SETTINGS_MODULE)

    @property
    def wrapped_settings(self):
        if django.VERSION[:2] < (1, 1):
            wrapped = '_target'
        else:
            wrapped = '_wrapped'
        return wrapped

    def load_settings(self, module):
        old_module = os.environ['DJANGO_SETTINGS_MODULE']
        # remove old settings module
        if old_module in sys.modules:
            del sys.modules[old_module]
        # keep runtime settings
        if django.VERSION[:2] < (1, 1):
            extra_settings = {}
        else:
            extra_settings = {
                'DATABASE_NAME': settings.DATABASE_NAME,
                'DATABASE_SUPPORTS_TRANSACTIONS': getattr(
                    settings, 'DATABASE_SUPPORTS_TRANSACTIONS'),
            }
        # force django to reload its settings
        setattr(settings, self.wrapped_settings, None)
        # update settings module for next reload
        os.environ['DJANGO_SETTINGS_MODULE'] = module

        # synch extra settings
        for key, value in extra_settings.items():
            setattr(settings, key, value)

        return old_module

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


class SchemaConfigCommandTestCase(DjangoCommandTestCase):
    def setUp(self):
        config = """
[django]
database_engine = sqlite3
database_name = :memory:
installed_apps = django_settings
"""
        self.set_config(config)
        super(SchemaConfigCommandTestCase, self).setUp(
            'test_django_settings.settings_schemaconfig')

    def tearDown(self):
        super(SchemaConfigCommandTestCase, self).tearDown()

        os.remove('test.cfg')

    def set_config(self, config):
        config_file = open('test.cfg', 'w')
        config_file.write(config)
        config_file.close()

