# -*- coding: utf-8 -*-
# Copyright 2010 Canonical Ltd.  This software is licensed under the
# GNU Lesser General Public License version 3 (see the file LICENSE).

import unittest
from cStringIO import StringIO

from django_schemaconfig.utils import (update_settings, get_django_settings,
    SETTINGS_ENCODING)
from django_schemaconfig.schema import schemas, Django102Schema
from schemaconfig.options import (DictConfigOption, IntConfigOption,
    StringConfigOption)
from schemaconfig.parser import SchemaConfigParser, CONFIG_FILE_ENCODING
from schemaconfig.schema import Schema


class DjangoSupportTestCase(unittest.TestCase):
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
        expected = Django102Schema
        default = schemas.get(schemas._default)

        # test get valid version
        self.assertEqual(schemas.get('1.0.2'), expected)

        # test get invalid version
        self.assertEqual(schemas.get('1.1'), default)

