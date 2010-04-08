import django

from schemaconfig import SchemaConfigParser
from schemaconfig.django import update_settings, schemas


DjangoSchema = schemas.get(django.get_version())
# parse config file
parser = SchemaConfigParser(DjangoSchema())
parser.read(['test.cfg'])
update_settings(parser, locals())

# keep parser reference
__SCHEMACONFIGPARSER__ = parser

