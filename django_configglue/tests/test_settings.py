# Copyright 2010 Canonical Ltd.  This software is licensed under the
# GNU Lesser General Public License version 3 (see the file LICENSE).

import os.path

import django
from django import get_version
from django.conf import settings
from django.core.management import ManagementUtility

from django_configglue.utils import SETTINGS_ENCODING
from django_configglue.tests.helpers import ConfigGlueDjangoCommandTestCase


class SettingsCommandTestCase(ConfigGlueDjangoCommandTestCase):
    COMMAND = 'settings'

    def test_no_args(self):
        self.call_command()
        self.assertTrue(self.capture['stdout'].startswith('Usage: '))

    def test_get(self):
        self.call_command('installed_apps')
        expected_output = "INSTALLED_APPS = ['django_configglue']"
        self.assertEqual(self.capture['stdout'].strip(), expected_output)

    def test_get_not_found(self):
        self.call_command('bogus')
        expected_output = "setting BOGUS not found"
        self.assertEqual(self.capture['stdout'].strip(), expected_output)

    def test_show(self):
        expected_values = [
            "ROOT_URLCONF = 'urls'",
            "SITE_ID = 1",
            "SETTINGS_MODULE = 'django_configglue.tests.settings'",
            "SETTINGS_ENCODING = '%s'" % SETTINGS_ENCODING,
        ]
        django_version = django.VERSION[:2]
        if django_version == (1, 1):
            expected_values.append("DATABASE_SUPPORTS_TRANSACTIONS = True")
        if django_version >= (1, 1):
            expected_values.append("JING_PATH = '/usr/bin/jing'")
        self.call_command(show_current=True)
        output_lines = self.capture['stdout'].strip().split('\n')
        self.assertEqual(set(expected_values), set(output_lines))

    def test_show_global(self):
        self.call_command(show_current=True, include_global=True)
        expected_output = dict([(key, getattr(settings, key)) for key in
            dir(settings) if self.is_setting(key)])
        # process output into dictionary
        items = map(lambda x: x.split(' = '),
                    self.capture['stdout'].strip().split('\n'))
        items = map(lambda x: (x[0].strip(), eval(x[1].strip())),
            (t for t in items if self.is_setting(t[0])))
        output = dict(items)
        # test equality
        self.assertEqual(output, expected_output)

    def test_locate_setting(self):
        self.call_command('time_zone', locate=True)
        location = os.path.join(os.path.realpath(os.path.curdir), 'test.cfg')
        expected_output = "setting TIME_ZONE last defined in '%s'" % location
        self.assertEqual(self.capture['stdout'].strip(), expected_output)

    def test_locate_setting_not_found(self):
        self.call_command('bogus', locate=True)
        expected_output = 'setting BOGUS not found'
        self.assertEqual(self.capture['stdout'].strip(), expected_output)

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
            self.assertEqual(self.capture['stdout'].strip(), expected_output)
        finally:
            wrapped.__CONFIGGLUE_PARSER__ = old_CONFIGGLUE_PARSER

    def test_locate_setting_not_found_no_configglue_parser(self):
        wrapped = getattr(settings, self.wrapped_settings)
        old_CONFIGGLUE_PARSER = wrapped.__CONFIGGLUE_PARSER__
        del wrapped.__CONFIGGLUE_PARSER__

        try:
            self.call_command('bogus', locate=True)
            expected_output = 'setting BOGUS not found'
            self.assertEqual(self.capture['stdout'].strip(), expected_output)
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


class ValidateCommandTestCase(ConfigGlueDjangoCommandTestCase):
    COMMAND = 'settings'

    def test_valid_config(self):
        self.call_command(validate=True)
        expected_output = 'Settings appear to be fine.'
        self.assertEqual(self.capture['stdout'].strip(), expected_output)

    def test_invalid_config(self):
        config = """
[bogus]
invalid_setting = foo
"""
        self.set_config(config)
        self.load_settings()
        self.assertRaises(SystemExit, self.call_command, validate=True)

        try:
            self.call_command(validate=True)
        except SystemExit, e:
            self.assertEqual(e.code, 1)
            error_msg = 'Error: Settings did not validate against schema.'
            self.assertTrue(self.capture['stderr'].strip().startswith(
                error_msg))

    def test_no_configglue_parser(self):
        wrapped = getattr(settings, self.wrapped_settings)
        old_CONFIGGLUE_PARSER = wrapped.__CONFIGGLUE_PARSER__
        del wrapped.__CONFIGGLUE_PARSER__

        try:
            self.call_command(validate=True)
            expected_output = ('The settings module was not generated by '
                'configglue. Can only validate configglue generated settings.')
            self.assertEqual(self.capture['stdout'].strip(), expected_output)
        finally:
            wrapped.__CONFIGGLUE_PARSER__ = old_CONFIGGLUE_PARSER


class CommandLineIntegrationTestCase(ConfigGlueDjangoCommandTestCase):
    COMMAND = 'settings'

    def test_help(self):
        self.call_command()
        self.assertTrue('--django_debug' in self.capture['stdout'])

    def test_update_settings(self):
        self.assertTrue(settings.DEBUG)
        args = ['manage.py', 'settings', '--django_debug=False', 'DEBUG']
        utility = ManagementUtility(argv=args)
        self.begin_capture()
        try:
            utility.execute()
        finally:
            self.end_capture()
        self.assertTrue('False' in self.capture['stdout'])

    def test_version_is_printed_once(self):
        args = ['manage.py', '--version']
        utility = ManagementUtility(argv=args)
        self.begin_capture()
        try:
            utility.execute()
        finally:
            self.end_capture()
        expected = get_version()
        self.assertTrue(self.capture['stdout'].count(expected) == 1)

    def test_noargs_doesnt_error(self):
        args = ['manage.py']
        utility = ManagementUtility(argv=args)
        self.begin_capture()
        try:
            self.assertRaises(SystemExit, utility.execute)
        finally:
            self.end_capture()
        self.assertFalse('Unknown command' in self.capture['stdout'])
