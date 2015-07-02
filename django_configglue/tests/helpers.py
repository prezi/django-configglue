# Copyright 2010-2011 Canonical Ltd.  This software is licensed under the
# GNU Lesser General Public License version 3 (see the file LICENSE).

import logging
import os
import sys
import textwrap
from StringIO import StringIO

import django
from django.core import management
from django.conf import settings
from django.test import TestCase
try:
    from django.utils.functional import empty
except ImportError:
    empty = None

from configglue.schema import (
    ListOption,
    TupleOption,
    Schema,
)

BELOW_DJANGO_1_8_CONDITION = django.VERSION[:2] >= (1, 8)
BELOW_DJANGO_1_8_ERROR = 'Does not apply to Django 1.8 and up.'


class ConfigGlueDjangoCommandTestCase(TestCase):
    COMMAND = ''

    def setUp(self):
        super(ConfigGlueDjangoCommandTestCase, self).setUp()
        # disable logging during tests
        self.level = logging.getLogger().level
        logging.disable(logging.ERROR)

        config = textwrap.dedent("""
            [django]
            installed_apps = django_configglue
            time_zone = Europe/London
            databases = databases

            [databases]
            default = db_default

            [db_default]
            engine = django.db.backends.sqlite3
            name = :memory:
        """)

        self.set_config(config)
        self._DJANGO_SETTINGS_MODULE = self.load_settings()

    def tearDown(self):
        # re-enable logging
        logging.getLogger().setLevel(self.level)

        self.load_settings(self._DJANGO_SETTINGS_MODULE)
        self.assertEqual(os.environ['DJANGO_SETTINGS_MODULE'],
                         self._DJANGO_SETTINGS_MODULE)

        os.remove('test.cfg')
        super(ConfigGlueDjangoCommandTestCase, self).tearDown()

    def set_config(self, config):
        config_file = open('test.cfg', 'w')
        config_file.write(config)
        config_file.close()

    @property
    def wrapped_settings(self):
        # make sure the wrapped object is not None
        # by just querying it for a setting
        getattr(settings, 'DEBUG', False)
        assert(getattr(settings, '_wrapped') is not empty)
        return '_wrapped'

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
        # save _original_allowed_hosts so that the teardown will work
        # properly
        _original_allowed_hosts = getattr(
            settings, '_original_allowed_hosts', None)
        # force django to reload its settings
        setattr(settings, self.wrapped_settings, empty)
        # update settings module for next reload
        os.environ['DJANGO_SETTINGS_MODULE'] = module

        # synch extra settings
        for key, value in extra_settings.items():
            setattr(settings, key, value)

        settings._original_allowed_hosts = _original_allowed_hosts

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

        self.output = sys.stdout.read() + sys.stderr.read()

        sys.stdout = self._stdout
        sys.stderr = self._stderr

    def call_command(self, *args, **kwargs):
        self.begin_capture()
        try:
            management.call_command(self.COMMAND, *args, **kwargs)
        finally:
            self.end_capture()


class SchemaHelperTestCase(TestCase):
    def setUp(self):
        super(SchemaHelperTestCase, self).setUp()
        # disable logging during tests
        self.level = logging.getLogger().level
        logging.disable(logging.ERROR)

    def tearDown(self):
        # re-enable logging
        logging.getLogger().setLevel(self.level)
        super(SchemaHelperTestCase, self).tearDown()

    def assert_schema_structure(self, schema_cls, version, options):
        self.assertTrue(issubclass(schema_cls, Schema))
        self.assertEqual(schema_cls.version, version)

        schema = schema_cls()

        # assert sections
        section_names = [section.name for section in schema.sections()]
        self.assertEqual(section_names, ['django'])
        # assert options for django section
        option_names = [option.name for option in schema.options('django')]
        self.assertEqual(option_names, options.keys())
        # assert options
        for name, value in options.items():
            option = schema.section('django').option(name)
            self.assertEqual(type(option), type(value))
            self.assertEqual(option.default, value.default)

    def assert_schemas_equal(self, this, other):
        # compare schemas
        this_sections = sorted(
            [section.name for section in this.sections()])
        other_sections = sorted(
            [section.name for section in other.sections()])
        self.assertEqual(this_sections, other_sections)
        self.assertEqual(this_sections, ['django'])

        # compare options
        section = this.section('django')
        expected_section = other.section('django')
        options = section.options()

        this_options = sorted(
            [option.name for option in options])
        other_options = sorted(
            [option.name for option in expected_section.options()])
        self.assertEqual(this_options, other_options)

        for option in options:
            expected_option = expected_section.option(option.name)
            # handle special case for list/tuple
            # django defaults to tuples for options it defines as lists
            if (isinstance(option, (ListOption, TupleOption)) or
                    isinstance(expected_option, (ListOption, TupleOption))):
                if option.default is None:
                    self.assertIsNone(expected_option.default)
                else:
                    self.assertEqual(list(option.default),
                                     list(expected_option.default))
            else:
                self.assertEqual(option.default,
                    expected_option.default)
