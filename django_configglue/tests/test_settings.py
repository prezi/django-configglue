# Copyright 2010-2011 Canonical Ltd.  This software is licensed under the
# GNU Lesser General Public License version 3 (see the file LICENSE).

import os.path
from unittest import skipIf

import django
from django import get_version
from django.conf import settings
from django.core.management import CommandError

from mock import patch, Mock

from django_configglue.management import GlueManagementUtility
from django_configglue.utils import SETTINGS_ENCODING
from django_configglue.schema import schemas
from django_configglue.tests.helpers import (
    ConfigGlueDjangoCommandTestCase,
    SchemaHelperTestCase,
    BELOW_DJANGO_1_8_CONDITION,
    BELOW_DJANGO_1_8_ERROR
)


class SettingsCommandTestCase(ConfigGlueDjangoCommandTestCase):
    COMMAND = 'settings'

    def test_no_args(self):
        self.call_command()
        self.assertTrue(self.output.startswith('Usage: '))

    def test_get(self):
        self.call_command('installed_apps')
        expected_output = "INSTALLED_APPS = ['django_configglue']"
        self.assertEqual(self.output.strip(), expected_output)

    def test_get_not_found(self):
        self.call_command('bogus')
        expected_output = "setting BOGUS not found"
        self.assertEqual(self.output.strip(), expected_output)

    def test_show(self):
        expected_values = [
            'SITE_ID = 1',
            "SETTINGS_MODULE = 'django_configglue.tests.settings'",
            "ROOT_URLCONF = 'urls'",
            "SETTINGS_ENCODING = '%s'" % SETTINGS_ENCODING,
        ]
        # Django 1.6 needs special treatment (BASE_DIR is not a core setting,
        # but it's a very useful convention from the example project)
        if django.VERSION >= (1, 6, 0):
            expected_values.append("BASE_DIR = ''")
        self.call_command(show_current=True)
        output_lines = self.output.strip().split('\n')
        self.assertEqual(set(expected_values), set(output_lines))

    def test_show_global(self):
        self.call_command(show_current=True, include_global=True)
        expected_output = dict([(key, getattr(settings, key)) for key in
            dir(settings) if self.is_setting(key)])
        # process output into dictionary
        items = map(lambda x: x.split(' = '),
                    self.output.strip().split('\n'))
        items = map(lambda x: (x[0].strip(), eval(x[1].strip())),
            (t for t in items if self.is_setting(t[0])))
        output = dict(items)
        # test equality
        self.assertEqual(output, expected_output)

    @skipIf(BELOW_DJANGO_1_8_CONDITION, BELOW_DJANGO_1_8_ERROR)
    def test_locate_setting(self):
        self.call_command('time_zone', locate=True)
        location = os.path.join(os.path.realpath(os.path.curdir), 'test.cfg')
        expected_output = "setting TIME_ZONE last defined in '%s'" % location
        self.assertEqual(self.output.strip(), expected_output)

    @skipIf(BELOW_DJANGO_1_8_CONDITION, BELOW_DJANGO_1_8_ERROR)
    def test_locate_setting_not_found(self):
        self.call_command('bogus', locate=True)
        expected_output = 'setting BOGUS not found'
        self.assertEqual(self.output.strip(), expected_output)

    @skipIf(BELOW_DJANGO_1_8_CONDITION, BELOW_DJANGO_1_8_ERROR)
    def test_locate_setting_no_configglue_parser(self):
        wrapped = getattr(settings, self.wrapped_settings)
        old_CONFIGGLUE_PARSER = wrapped.__CONFIGGLUE_PARSER__
        del wrapped.__CONFIGGLUE_PARSER__

        try:
            self.call_command('time_zone', locate=True)
            mod = __import__('django_configglue.tests.settings', globals(),
                             locals(), [''])
            location = os.path.realpath(mod.__file__)
            expected_output = "setting TIME_ZONE last defined in %r" % location
            self.assertEqual(self.output.strip(), expected_output)
        finally:
            wrapped.__CONFIGGLUE_PARSER__ = old_CONFIGGLUE_PARSER

    @skipIf(BELOW_DJANGO_1_8_CONDITION, BELOW_DJANGO_1_8_ERROR)
    def test_locate_setting_not_found_no_configglue_parser(self):
        wrapped = getattr(settings, self.wrapped_settings)
        old_CONFIGGLUE_PARSER = wrapped.__CONFIGGLUE_PARSER__
        del wrapped.__CONFIGGLUE_PARSER__

        try:
            self.call_command('bogus', locate=True)
            expected_output = 'setting BOGUS not found'
            self.assertEqual(self.output.strip(), expected_output)
        finally:
            wrapped.__CONFIGGLUE_PARSER__ = old_CONFIGGLUE_PARSER

    def test_wrapped_settings(self):
        # the settings object has a _target attribute
        # this is true for versions of django <= 1.0.2
        expected = '_target'
        if django.VERSION[:3] > (1, 0, 2):
            # the settings object has a _wrapped attribute
            # this is true for versions of django > 1.0.2
            expected = '_wrapped'

        self.assertEqual(self.wrapped_settings, expected)


class GeneratedSettingsTestCase(ConfigGlueDjangoCommandTestCase,
        SchemaHelperTestCase):
    def setUp(self):
        super(GeneratedSettingsTestCase, self).setUp()
        self.expected_schema = schemas.get(
            django.get_version(), strict=True)()
        self.version = '.'.join(django.get_version().split('.')[:2]) + '.foo'
        mock_get_version = Mock(return_value=self.version)
        self.patch_get_version = patch(
            'django_configglue.tests.settings.django.get_version',
            mock_get_version)
        self.patch_get_version.start()
        self.mock_warn = Mock()
        self.patch_warn = patch(
            'django_configglue.schema.logging.warn', self.mock_warn)
        self.patch_warn.start()

    def tearDown(self):
        self.patch_get_version.stop()
        self.patch_warn.stop()
        super(GeneratedSettingsTestCase, self).tearDown()

    def test_generated_schema(self):
        # import here so that the necessary modules can be mocked before
        # being required
        self.load_settings()

        from django.conf import settings
        schema = settings.__CONFIGGLUE_PARSER__.schema

        self.assert_schemas_equal(schema, self.expected_schema)
        self.assertEqual(self.mock_warn.call_args_list,
            [(("No schema registered for version '%s'" % self.version,),
              {}),
             (("Dynamically creating schema for version '%s'" % self.version,),
              {})])


class ValidateCommandTestCase(ConfigGlueDjangoCommandTestCase):
    COMMAND = 'settings'

    def test_valid_config(self):
        try:
            self.call_command(validate=True)
        except SystemExit:
            pass
        expected_output = 'Settings appear to be fine.'
        self.assertEqual(self.output.strip(), expected_output)

    def test_invalid_config(self):
        config = """
[bogus]
invalid_setting = foo
"""
        self.set_config(config)
        self.load_settings()

        try:
            self.call_command(validate=True)
        except (SystemExit, CommandError), e:
            error_msg = 'Settings did not validate against schema.'
            self.assertTrue((error_msg in self.output.strip()) or
                            error_msg in str(e))

    @skipIf(BELOW_DJANGO_1_8_CONDITION, BELOW_DJANGO_1_8_ERROR)
    def test_no_configglue_parser(self):
        wrapped = getattr(settings, self.wrapped_settings)
        old_CONFIGGLUE_PARSER = wrapped.__CONFIGGLUE_PARSER__
        del wrapped.__CONFIGGLUE_PARSER__

        try:
            self.call_command(validate=True)
            expected_output = ('The settings module was not generated by '
                'configglue. Can only validate configglue generated settings.')
            self.assertEqual(self.output.strip(), expected_output)
        finally:
            wrapped.__CONFIGGLUE_PARSER__ = old_CONFIGGLUE_PARSER


class CommandLineIntegrationTestCase(ConfigGlueDjangoCommandTestCase):
    COMMAND = 'settings'

    def test_help(self):
        self.call_command()
        self.assertTrue('--django_debug' in self.output)

    @skipIf(BELOW_DJANGO_1_8_CONDITION, BELOW_DJANGO_1_8_ERROR)
    def test_update_settings(self):
        self.assertTrue(settings.DEBUG)
        args = ['manage.py', 'settings', '--django_debug=False', 'DEBUG']
        utility = GlueManagementUtility(argv=args)
        self.begin_capture()
        try:
            utility.execute()
        finally:
            self.end_capture()
        self.assertTrue('False' in self.output)

    @skipIf(BELOW_DJANGO_1_8_CONDITION, BELOW_DJANGO_1_8_ERROR)
    def test_version_is_printed_once(self):
        args = ['manage.py', '--version']
        utility = GlueManagementUtility(argv=args)
        self.begin_capture()
        try:
            utility.execute()
        finally:
            self.end_capture()
        expected = get_version()
        self.assertEqual(1, self.output.count(expected))

    @skipIf(BELOW_DJANGO_1_8_CONDITION, BELOW_DJANGO_1_8_ERROR)
    def test_noargs_doesnt_error(self):
        args = ['manage.py']
        utility = GlueManagementUtility(argv=args)
        self.begin_capture()
        try:
            utility.execute()
        except SystemExit:
            # Django <= 1.3 uses SystemExit to terminate management
            # command
            pass
        finally:
            self.end_capture()
        self.assertFalse('Unknown command' in self.output)
