# Copyright 2010 Canonical Ltd.  This software is licensed under the
# GNU Lesser General Public License version 3 (see the file LICENSE).

import os
import sys
import textwrap
from StringIO import StringIO

import django
from django.core import management
from django.conf import settings
from django.test import TestCase


class ConfigGlueDjangoCommandTestCase(TestCase):
    COMMAND = ''

    def setUp(self):
        config = textwrap.dedent("""
            [django]
            database_engine = sqlite3
            database_name = :memory:
            installed_apps = django_configglue
            time_zone = Europe/London
        """)

        if django.VERSION[:2] > (1, 1):
            # since 1.2 use multi database settings format
            config += textwrap.dedent("""
                databases = databases

                [databases]
                default = db_default

                [db_default]
                engine = sqlite3
                name = :memory:
            """)

        self.set_config(config)
        self._DJANGO_SETTINGS_MODULE = self.load_settings()

    def tearDown(self):
        self.load_settings(self._DJANGO_SETTINGS_MODULE)
        self.assertEqual(os.environ['DJANGO_SETTINGS_MODULE'],
                         self._DJANGO_SETTINGS_MODULE)

        os.remove('test.cfg')

    def set_config(self, config):
        config_file = open('test.cfg', 'w')
        config_file.write(config)
        config_file.close()

    @property
    def wrapped_settings(self):
        wrapped = '_target'
        if django.VERSION[:3] > (1, 0, 2):
            wrapped = '_wrapped'
        # make sure the wrapped object is not None
        # by just querying it for a setting
        getattr(settings, 'DEBUG', False)
        assert(getattr(settings, wrapped) != None)
        return wrapped

    def load_settings(self, module='django_configglue.tests.settings'):
        old_module = os.environ['DJANGO_SETTINGS_MODULE']
        # remove old settings module
        if old_module in sys.modules:
            del sys.modules[old_module]
        # keep runtime settings
        extra_settings = {}
        if django.VERSION[:2] == (1, 1):
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

        if hasattr(self, 'extra_settings'):
            for key, value in self.extra_settings.items():
                setattr(settings, key, value)
        self.extra_settings = extra_settings

        return old_module

    def is_setting(self, name):
        return not name.startswith('__') and name.isupper()

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

