# -*- coding: utf-8 -*-
# Copyright 2010 Canonical Ltd.  This software is licensed under the
# GNU Lesser General Public License version 3 (see the file LICENSE).

import textwrap
from cStringIO import StringIO
from unittest import TestCase

import django
from configglue.pyschema.schema import (
    DictConfigOption,
    IntConfigOption,
    Schema,
    StringConfigOption,
)
from configglue.pyschema.parser import (
    CONFIG_FILE_ENCODING,
    SchemaConfigParser,
)
from django.conf import settings
from mock import patch

from django_configglue import GlueManagementUtility
from django_configglue.utils import (
    SETTINGS_ENCODING,
    configglue,
    get_django_settings,
    update_settings,
)
from django_configglue.schema import (
    BaseDjangoSchema,
    DjangoSchemaFactory,
    UpperCaseDictConfigOption,
    schemas,
)
from django_configglue.tests.helpers import ConfigGlueDjangoCommandTestCase


class DjangoSupportTestCase(TestCase):
    def test_get_django_settings(self):
        class MySchema(Schema):
            foo = IntConfigOption()
            bar = DictConfigOption(
                spec={'baz': IntConfigOption(),
                      'BAZ': IntConfigOption()})

        expected = {'FOO': 0, 'BAR': {'baz': 0, 'BAZ': 0}}

        parser = SchemaConfigParser(MySchema())
        result = get_django_settings(parser)
        self.assertEqual(result, expected)

    def test_get_django_settings_encoding(self):
        class MySchema(Schema):
            foo = StringConfigOption()

        expected = {'FOO': u'€'.encode(SETTINGS_ENCODING)}

        config = StringIO(u'[__main__]\nfoo=€'.encode(CONFIG_FILE_ENCODING))
        parser = SchemaConfigParser(MySchema())
        parser.readfp(config)
        self.assertEqual(parser.values('__main__'), {'foo': u'€'})
        result = get_django_settings(parser)
        self.assertEqual(result, expected)

    def test_update_settings(self):
        class MySchema(Schema):
            foo = IntConfigOption()

        env = {}
        parser = SchemaConfigParser(MySchema())
        update_settings(parser, env)
        expected_env = {
            'FOO': 0,
            'SETTINGS_ENCODING': SETTINGS_ENCODING,
            '__CONFIGGLUE_PARSER__': parser,
        }
        self.assertEqual(env, expected_env)

    def test_schemafactory_get(self):
        # test get valid version
        self.assertEqual(schemas.get('1.0.2 final'), BaseDjangoSchema)

        # test get invalid version
        self.assertRaises(ValueError, schemas.get, '1.1')

    @patch('django_configglue.schema.logging')
    def test_schemafactory_get_nonexisting_too_old(self, mock_logging):
        schema = schemas.get('0.96', strict=False)

        django_102 = schemas.get('1.0.2 final')
        self.assertEqual(schema, django_102)
        self.assertRaises(ValueError, schemas.get, '0.96')

        self.assertEqual(mock_logging.warn.call_args_list[0][0][0],
            "No schema registered for version '0.96'")
        self.assertEqual(mock_logging.warn.call_args_list[1][0][0],
            "Falling back to schema for version '1.0.2 final'")

    @patch('django_configglue.schema.logging')
    def test_schemafactory_get_nonexisting(self, mock_logging):
        schema = schemas.get('1.0.3', strict=False)

        django_102 = schemas.get('1.0.2 final')
        self.assertEqual(schema, django_102)
        self.assertRaises(ValueError, schemas.get, '1.0.3')

        self.assertEqual(mock_logging.warn.call_args_list[0][0][0],
            "No schema registered for version '1.0.3'")
        self.assertEqual(mock_logging.warn.call_args_list[1][0][0],
            "Falling back to schema for version '1.0.2 final'")

    @patch('django_configglue.schema.logging')
    def test_schemafactory_get_nonexisting_too_new(self, mock_logging):
        schema = schemas.get('1.2.0', strict=False)

        django_112 = schemas.get('1.1.4')
        self.assertEqual(schema, django_112)
        self.assertRaises(ValueError, schemas.get, '1.2.0')

        self.assertEqual(mock_logging.warn.call_args_list[0][0][0],
            "No schema registered for version '1.2.0'")
        self.assertEqual(mock_logging.warn.call_args_list[1][0][0],
            "Falling back to schema for version '1.1.4'")

    @patch('django_configglue.schema.logging')
    def test_schemafactory_get_no_versions_registered(self, mock_logging):
        schemas = DjangoSchemaFactory()
        try:
            schemas.get('1.0.2 final', strict=False)
        except ValueError, e:
            self.assertEqual(str(e), "No schemas registered")
        else:
            self.fail("ValueError not raised")

        mock_logging.warn.assert_called_with(
            "No schema registered for version '1.0.2 final'")

    def test_schema_versions(self):
        django_102 = schemas.get('1.0.2 final')()
        django_112 = schemas.get('1.1.2')()
        self.assertEqual(django_102.version, '1.0.2 final')
        self.assertEqual(django_112.version, '1.1.2')
        self.assertFalse(django_102 is django_112)

    def test_register_without_version(self):
        class MySchema(Schema):
            pass

        schemas = DjangoSchemaFactory()
        self.assertRaises(ValueError, schemas.register, MySchema)

    def test_configglue(self):
        target = {}
        schema = schemas.get(django.get_version(), strict=False)
        configglue(schema, [], target)
        # target is consistent with django's settings module
        # except for a few keys
        shared_key = lambda x: (not x.startswith('__') and x.upper() == x and
            x not in ('DATABASE_SUPPORTS_TRANSACTIONS', 'SETTINGS_MODULE'))
        expected_keys = set(filter(shared_key, dir(settings)))
        target_keys = set(filter(shared_key, target.keys()))

        self.assertEqual(expected_keys, target_keys)

    @patch('django_configglue.utils.update_settings')
    @patch('django_configglue.utils.SchemaConfigParser')
    def test_configglue_calls(self, MockSchemaConfigParser,
        mock_update_settings):

        target = {}
        configglue(BaseDjangoSchema, [], target)

        MockSchemaConfigParser.assert_called_with(BaseDjangoSchema())
        MockSchemaConfigParser.return_value.read.assert_called_with([])
        mock_update_settings.assert_called_with(
            MockSchemaConfigParser.return_value, target)


class GlueManagementUtilityTestCase(ConfigGlueDjangoCommandTestCase):
    def setUp(self):
        super(GlueManagementUtilityTestCase, self).setUp()

        self.util = GlueManagementUtility()

    def execute(self):
        self.begin_capture()
        try:
            self.util.execute()
        finally:
            self.end_capture()

    def test_execute_no_args(self):
        self.util.argv = ['']
        self.assertRaises(SystemExit, self.execute)
        self.assertEqual(self.capture['stderr'],
            "Type '%s help' for usage.\n" % self.util.prog_name)

    def test_execute_help(self):
        self.util.argv = ['', 'help']
        self.assertRaises(SystemExit, self.execute)
        self.assertTrue(self.util.main_help_text() in self.capture['stderr'])

    def test_execute_help_option(self):
        self.util.argv = ['', '--help']
        self.execute()
        self.assertTrue(self.util.main_help_text() in self.capture['stderr'])

    def test_execute_help_for_command(self):
        self.util.argv = ['', 'help', 'settings']
        self.execute()
        self.assertTrue('Show settings attributes' in self.capture['stdout'])

    def test_execute_version(self):
        from django import get_version
        self.util.argv = ['', '--version']
        self.execute()
        self.assertTrue(get_version() in self.capture['stdout'])

    def test_execute(self):
        self.util.argv = ['', 'settings']
        self.execute()
        self.assertTrue('Show settings attributes' in self.capture['stdout'])

    def test_execute_settings_exception(self):
        from django.conf import settings
        wrapped = getattr(settings, self.wrapped_settings)
        old_CONFIGGLUE_PARSER = wrapped.__CONFIGGLUE_PARSER__
        del wrapped.__CONFIGGLUE_PARSER__

        try:
            self.util.argv = ['', 'help']
            self.assertRaises(SystemExit, self.execute)
            self.assertTrue(self.util.main_help_text() in self.capture['stderr'])
        finally:
            wrapped.__CONFIGGLUE_PARSER__ = old_CONFIGGLUE_PARSER

    @patch('django_configglue.utils.update_settings')
    def test_execute_configglue_exception(self, mock_update_settings):
        mock_update_settings.side_effect = Exception()

        self.util.argv = ['', 'help']
        self.assertRaises(SystemExit, self.execute)
        self.assertTrue(self.util.main_help_text() in self.capture['stderr'])

    def test_execute_with_schema_options(self):
        self.util.argv = ['', '--django_debug=False', 'help', 'settings']
        self.execute()
        self.assertTrue('Show settings attributes' in self.capture['stdout'])


class UpperCaseDictConfigOptionTestCase(TestCase):
    def test_parse(self):
        class MySchema(Schema):
            foo = UpperCaseDictConfigOption()
        config = StringIO(textwrap.dedent("""
            [__main__]
            foo = mydict
            [mydict]
            bar = 42
        """))

        schema = MySchema()
        parser = SchemaConfigParser(schema)
        parser.readfp(config)
        result = schema.foo.parse('mydict', parser)

        self.assertEqual(result, {'BAR': '42'})

