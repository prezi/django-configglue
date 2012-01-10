import textwrap
from cStringIO import StringIO
from unittest import TestCase

from configglue.parser import SchemaConfigParser

from django_configglue.schema import BaseDjangoSchema


class DjangoSchemaTestCase(TestCase):
    def test_time_zone_is_null(self):
        config = StringIO(textwrap.dedent("""
            [django]
            time_zone = None
            """))

        parser = SchemaConfigParser(BaseDjangoSchema())
        parser.readfp(config)
        value = parser.values()['django']['time_zone']
        self.assertEqual(value, None)

