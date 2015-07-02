# -*- coding: utf-8 -*-
# Copyright 2010-2011 Canonical Ltd.  This software is licensed under the
# GNU Lesser General Public License version 3 (see the file LICENSE).

import inspect
import textwrap
from cStringIO import StringIO
from optparse import BadOptionError
from unittest import TestCase, skipIf

import django
from configglue.schema import (
    BoolOption,
    DictOption,
    IntOption,
    ListOption,
    Schema,
    Section,
    StringOption,
    TupleOption,
)
from configglue.parser import (
    CONFIG_FILE_ENCODING,
    SchemaConfigParser,
)
from django.conf import settings
from django.conf import global_settings
from mock import patch

from django_configglue import management
from django_configglue.utils import (
    SETTINGS_ENCODING,
    configglue,
    get_django_settings,
    update_settings,
    get_project_settings,
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
    BELOW_DJANGO_1_8_CONDITION,
    BELOW_DJANGO_1_8_ERROR
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
        self.assertEqual(
            schemas.get('1.0', strict=True),
            BaseDjangoSchema
        )

        # test get invalid version
        self.assertRaises(ValueError, schemas.get, '1.1.1', strict=True)

    def test_schema_versions(self):
        django_13 = schemas.get('1.3')()
        django_14 = schemas.get('1.4')()
        self.assertEqual(django_13.version, '1.3')
        self.assertEqual(django_14.version, '1.4')
        self.assertFalse(django_13 is django_14)

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
        exclude_keys = ['DATABASE_SUPPORTS_TRANSACTIONS', 'SETTINGS_MODULE']
        # CACHE_BACKEND has been removed from django 1.3 schema but is
        # added by django at runtime, so let's skip that too
        if schema.version >= '1.3':
            exclude_keys.append('CACHE_BACKEND')
        shared_key = lambda x: (not x.startswith('__') and x.upper() == x and
            x not in exclude_keys)
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

        for i, (opt_type, default) in enumerate(data):
            schema_cls = schemas.build('bogus.%d' % i, {'foo': default}, Schema)
            # do common checks
            self.assert_schema_structure(schema_cls, 'bogus.%d' % i,
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
            inspect.getmembers(get_project_settings()) if name.isupper()])
        # handle special case of ROOT_URLCONF which depends on the
        # project name
        root_urlconf = project_options['root_urlconf'].replace(
            '{{ project_name }}.', '')
        project_options['root_urlconf'] = root_urlconf

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

    def test_django13_caches(self):
        schema = schemas.get('1.3')
        expected = DictOption(
            item=UpperCaseDictOption(
                spec={
                    'backend': StringOption(),
                    'location': StringOption()}))
        self.assertEqual(schema.django.caches.item, expected.item)

    def test_django13_logging_config(self):
        schema = schemas.get('1.3')
        section = Section(name='django')
        expected = StringOption(name='logging_config', null=True,
            default='django.utils.log.dictConfig',
            help='The callable to use to configure logging')
        expected.section = section
        self.assertEqual(schema.django.logging_config, expected)

    def test_django13_null_logging_config(self):
        config = StringIO(textwrap.dedent("""
            [django]
            logging_config = None
            """))

        schema = schemas.get('1.3')
        parser = SchemaConfigParser(schema())
        parser.readfp(config)
        value = parser.values()['django']['logging_config']
        self.assertEqual(value, None)

    def test_django13_custom_logging_config(self):
        config = StringIO(textwrap.dedent("""
            [django]
            logging_config = foo
            """))

        schema = schemas.get('1.3')
        parser = SchemaConfigParser(schema())
        parser.readfp(config)
        value = parser.values()['django']['logging_config']
        self.assertEqual(value, 'foo')

    def test_django13_logging_default(self):
        expected = {
            'version': 1,
            'handlers': {
                'mail_admins': {
                    'class': 'django.utils.log.AdminEmailHandler',
                    'level': 'ERROR'}},
            'loggers': {
                'django.request': {
                    'handlers': ['mail_admins'],
                    'level': 'ERROR',
                    'propagate': True}},
            'disable_existing_loggers': False,
        }

        schema = schemas.get('1.3')
        self.assertEqual(schema().django.logging.default, expected)


class GlueManagementUtilityTestCase(ConfigGlueDjangoCommandTestCase):
    def setUp(self):
        super(GlueManagementUtilityTestCase, self).setUp()

        self.util = management.GlueManagementUtility()

    def execute(self):
        self.begin_capture()
        try:
            self.util.execute()
        finally:
            self.end_capture()

    @skipIf(BELOW_DJANGO_1_8_CONDITION, BELOW_DJANGO_1_8_ERROR)
    def test_execute_no_args(self):
        self.util.argv = ['']
        try:
            self.execute()
        except SystemExit:
            pass
        self.assertTrue(
            "Type '%s help <subcommand>' for help" % (self.util.prog_name,) in
            self.output)

    @skipIf(BELOW_DJANGO_1_8_CONDITION, BELOW_DJANGO_1_8_ERROR)
    @patch('sys.stdout')
    def test_execute_help(self, mock_stdout):
        mock_stdout.isatty.return_value = False
        self.util.argv = ['', 'help']
        try:
            self.execute()
        except SystemExit:
            # In earlier versions than 1.4, help was raising SystemExit
            pass
        self.assertTrue(self.util.main_help_text() in self.output)

    @skipIf(BELOW_DJANGO_1_8_CONDITION, BELOW_DJANGO_1_8_ERROR)
    @patch('sys.stdout')
    def test_execute_help_option(self, mock_stdout):
        mock_stdout.isatty.return_value = False
        self.util.argv = ['', '--help']
        self.execute()
        self.assertTrue(self.util.main_help_text() in self.output)

    @skipIf(BELOW_DJANGO_1_8_CONDITION, BELOW_DJANGO_1_8_ERROR)
    def test_execute_help_for_command(self):
        self.util.argv = ['', 'help', 'settings']
        self.execute()
        self.assertTrue('Show settings attributes' in self.output)

    @skipIf(BELOW_DJANGO_1_8_CONDITION, BELOW_DJANGO_1_8_ERROR)
    def test_execute_version(self):
        from django import get_version
        self.util.argv = ['', '--version']
        self.execute()
        self.assertTrue(get_version() in self.output)

    @skipIf(BELOW_DJANGO_1_8_CONDITION, BELOW_DJANGO_1_8_ERROR)
    def test_execute(self):
        self.util.argv = ['', 'settings']
        self.execute()
        self.assertTrue('Show settings attributes' in self.output)

    @skipIf(BELOW_DJANGO_1_8_CONDITION, BELOW_DJANGO_1_8_ERROR)
    @patch('sys.stdout')
    def test_execute_settings_exception(self, mock_stdout):
        mock_stdout.isatty.return_value = False

        from django.conf import settings
        wrapped = getattr(settings, self.wrapped_settings)
        old_CONFIGGLUE_PARSER = wrapped.__CONFIGGLUE_PARSER__
        del wrapped.__CONFIGGLUE_PARSER__

        try:
            self.util.argv = ['', 'help']
            try:
                self.execute()
            except SystemExit:
                pass
            self.assertTrue(
                self.util.main_help_text() in self.output)
        finally:
            wrapped.__CONFIGGLUE_PARSER__ = old_CONFIGGLUE_PARSER

    @skipIf(BELOW_DJANGO_1_8_CONDITION, BELOW_DJANGO_1_8_ERROR)
    def test_execute_with_schema_options(self):
        self.util.argv = ['', '--django_debug=False', 'help', 'settings']
        self.execute()
        self.assertTrue('Show settings attributes' in self.output)

    @skipIf(BELOW_DJANGO_1_8_CONDITION, BELOW_DJANGO_1_8_ERROR)
    def test_verbosity_is_preserved(self):
        self.util.argv = ['', 'settings', '--verbosity=2']
        handle_path = ('django_configglue.management.commands.settings.'
                       'Command.handle')
        with patch(handle_path) as mock_handle:
            self.execute()
            args, options = mock_handle.call_args
            self.assertEqual('2', options['verbosity'])


class LaxOptionParserTestCase(TestCase):

    def test_explicit_value_for_unknown_option(self):
        parser = management.LaxOptionParser()
        rargs = ["--foo=bar"]
        self.assertRaises(BadOptionError, parser._process_long_opt, rargs, [])
        self.assertEqual([], rargs)


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


class ManagementTestCase(TestCase):
    def test_django_13_management_utility(self):
        with patch.object(django, 'VERSION', (1, 3)):
            # force reloading of module
            reload(management)

            self.assertEqual(management.management.ManagementUtility,
                             management.GlueManagementUtility)

    def test_django_14_management_utility(self):
        with patch.object(django, 'VERSION', (1, 4)):
            # force reloading of module
            reload(management)

            self.assertEqual(management.management.ManagementUtility,
                             django.core.management.ManagementUtility)

    def test_execute_from_command_line(self):
        name = 'django_configglue.management.GlueManagementUtility'
        with patch(name) as mock_utility:
            management.execute_from_command_line()
            mock_utility.assert_called_once_with(None)
