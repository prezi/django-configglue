# -*- coding: utf-8 -*-
# Copyright 2010 Canonical Ltd.  This software is licensed under the
# GNU Lesser General Public License version 3 (see the file LICENSE).

import inspect
import textwrap
from cStringIO import StringIO
from unittest import TestCase

import django
from configglue.pyschema.schema import (
    BoolOption,
    DictOption,
    IntOption,
    ListOption,
    Schema,
    Section,
    StringOption,
    TupleOption,
)
from configglue.pyschema.parser import (
    CONFIG_FILE_ENCODING,
    SchemaConfigParser,
)
from django.conf import settings
from django.conf import global_settings
from django.conf.project_template import settings as project_settings
from mock import patch

from django_configglue.management import GlueManagementUtility
from django_configglue.utils import (
    SETTINGS_ENCODING,
    configglue,
    get_django_settings,
    update_settings,
)
from django_configglue.schema import (
    BaseDjangoSchema,
    DjangoSchemaFactory,
    UpperCaseDictOption,
    schemas,
    derivate_django_schema,
)
from django_configglue.tests.helpers import (
    ConfigGlueDjangoCommandTestCase,
    SchemaHelperTestCase,
)


class DjangoSupportTestCase(SchemaHelperTestCase):
    def test_get_django_settings(self):
        class MySchema(Schema):
            foo = IntOption()
            bar = DictOption(
                spec={'baz': IntOption(),
                      'BAZ': IntOption()})

        expected = {'FOO': 0, 'BAR': {'baz': 0, 'BAZ': 0}}

        parser = SchemaConfigParser(MySchema())
        result = get_django_settings(parser)
        self.assertEqual(result, expected)

    def test_get_django_settings_encoding(self):
        class MySchema(Schema):
            foo = StringOption()

        expected = {'FOO': u'€'.encode(SETTINGS_ENCODING)}

        config = StringIO(u'[__main__]\nfoo=€'.encode(CONFIG_FILE_ENCODING))
        parser = SchemaConfigParser(MySchema())
        parser.readfp(config)
        self.assertEqual(parser.values('__main__'), {'foo': u'€'})
        result = get_django_settings(parser)
        self.assertEqual(result, expected)

    def test_update_settings(self):
        class MySchema(Schema):
            foo = IntOption()

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
        self.assertEqual(schemas.get('1.0.2 final', strict=True),
            BaseDjangoSchema)

        # test get invalid version
        self.assertRaises(ValueError, schemas.get, '1.1', strict=True)

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

    def test_schemafactory_build(self):
        schemas = DjangoSchemaFactory()

        data = [
            (IntOption, 1),
            (BoolOption, True),
            (TupleOption, (1, 2)),
            (ListOption, [1, 2]),
            (DictOption, {'a': 1}),
            (StringOption, 'foo'),
        ]

        for opt_type, default in data:
            schema_cls = schemas.build('bogus', {'foo': default})
            # do common checks
            self.assert_schema_structure(schema_cls, 'bogus',
                {'foo': opt_type(name='foo', default=default)})

    def test_schemafactory_build_django(self):
        schemas = DjangoSchemaFactory()

        schema = schemas.build()
        # get known django schema
        # fail for unknown versions of django
        django_schema = schemas.get(django.get_version(), strict=True)

        self.assert_schemas_equal(schema(), django_schema())

    def test_schemafactory_get_django(self):
        schemas = DjangoSchemaFactory()

        # build a django schema
        # get only django settings
        options = dict([(name, value) for (name, value) in
            inspect.getmembers(settings) if name.isupper()])
        schema = schemas.build(django.get_version(), options)
        # get known django schema
        # fail for unknown versions of django
        django_schema = schemas.get(django.get_version(), strict=True)

        self.assert_schemas_equal(schema(), django_schema())

    def test_schemafactory_build_complex_options(self):
        schemas = DjangoSchemaFactory()

        options = {
            'dict1': {'foo': 1, 'bar': '2'},
            'dict2': {'foo': {'bar': 2, 'baz': 3}},
            'list1': ['1', '2', '3'],
            'list2': [1, 2, 3],
        }
        expected = {
            'dict1': DictOption(name='dict1', default=options['dict1'],
                                item=StringOption()),
            'dict2': DictOption(name='dict2', default=options['dict2'],
                                item=DictOption()),
            'list1': ListOption(name='list1', default=options['list1'],
                                item=StringOption()),
            'list2': ListOption(name='list2', default=options['list2'],
                                item=IntOption()),
        }

        schema = schemas.build('foo', options)()

        sections = sorted(
            [section.name for section in schema.sections()])
        section = schema.section('django')
        self.assertEqual(sections, ['django'])

        for name in options:
            option = expected[name]
            option.section = section
            self.assertEqual(section.option(name), option)
            self.assertEqual(section.option(name).item, option.item)

    @patch('django_configglue.schema.logging')
    def test_schemafactory_get_unknown_build(self, mock_logging):
        schemas = DjangoSchemaFactory()
        version_string = django.get_version()
        self.assertFalse(version_string in schemas._schemas)

        # build schema
        schema = schemas.get(version_string, strict=False)()
        # get expected schema
        options = dict([(name.lower(), value) for (name, value) in
            inspect.getmembers(global_settings) if name.isupper()])
        project_options = dict([(name.lower(), value) for (name, value) in
            inspect.getmembers(project_settings) if name.isupper()])
        options.update(project_options)
        expected = schemas.build(django.get_version(), options)()

        # compare schemas
        self.assert_schemas_equal(schema, expected)

        self.assertEqual(mock_logging.warn.call_args_list[0][0][0],
            "No schema registered for version '{0}'".format(version_string))
        self.assertEqual(mock_logging.warn.call_args_list[1][0][0],
            "Dynamically creating schema for version '{0}'".format(
                version_string))

    def test_derivate_django_schema(self):
        class Parent(Schema):
            version = 'parent'

            class django(Section):
                foo = IntOption()
                bar = IntOption()

        class Child(Parent):
            version = 'parent'

            class django(Section):
                bar = IntOption()

        derivated = derivate_django_schema(Parent, exclude=['foo'])
        self.assert_schemas_equal(derivated(), Child())

    def test_derivate_django_schema_no_exclude(self):
        class Parent(Schema):
            version = 'parent'

            class django(Section):
                foo = IntOption()

        derivated = derivate_django_schema(Parent)
        self.assertEqual(derivated, Parent)


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
            self.assertTrue(
                self.util.main_help_text() in self.capture['stderr'])
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


class UpperCaseDictOptionTestCase(TestCase):
    def test_parse(self):
        class MySchema(Schema):
            foo = UpperCaseDictOption()
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
