# -*- coding: utf-8 -*-
# Copyright 2010 Canonical Ltd.  This software is licensed under the
# GNU Lesser General Public License version 3 (see the file LICENSE).

from cStringIO import StringIO
from mock import patch
from unittest import TestCase

from configglue.pyschema.options import (DictConfigOption, IntConfigOption,
    StringConfigOption)
from configglue.pyschema.parser import SchemaConfigParser, CONFIG_FILE_ENCODING
from configglue.pyschema.schema import Schema
from django_configglue import GlueManagementUtility
from django_configglue.utils import (update_settings, get_django_settings,
    SETTINGS_ENCODING)
from django_configglue.schema import (schemas, BaseDjangoSchema,
    Django102Schema, DjangoSchemaFactory)
from django_configglue.tests.helpers import ConfigGlueDjangoCommandTestCase


class DjangoSupportTestCase(TestCase):
    def test_get_django_settings(self):
        class MySchema(Schema):
            foo = IntConfigOption()
            bar = DictConfigOption({'baz': IntConfigOption(),
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

        expected_env = {'FOO': 0}

        env = {}
        parser = SchemaConfigParser(MySchema())
        update_settings(parser, env)
        self.assertEqual(env, expected_env)

    def test_schemafactory_get(self):
        # test get valid version
        self.assertEqual(schemas.get('1.0.2'), Django102Schema)

        # test get invalid version
        self.assertRaises(ValueError, schemas.get, '1.1')

    def test_schema_versions(self):
        django_102 = schemas.get('1.0.2')()
        django_112 = schemas.get('1.1.2')()
        self.assertEqual(django_102.version, '1.0.2')
        self.assertTrue(hasattr(django_102.django, 'jing_path'))
        self.assertEqual(django_112.version, '1.1.2')
        self.assertFalse(hasattr(django_112.django, 'jing_path'))

    def test_register_without_version(self):
        class MySchema(BaseDjangoSchema):
            pass

        schemas = DjangoSchemaFactory()
        self.assertRaises(ValueError, schemas.register, MySchema)


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

