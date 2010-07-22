import django
from schemaconfig import SchemaConfigParser
from django_schemaconfig.utils import update_settings
from django_schemaconfig.schema import schemas


DjangoSchema = schemas.get(django.get_version())
# parse config file
parser = SchemaConfigParser(DjangoSchema())
parser.read(['main.cfg', 'test.cfg'])
update_settings(parser, locals())

# keep parser reference
__SCHEMACONFIGPARSER__ = parser

