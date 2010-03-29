from schemaconfig import SchemaConfigParser
from schemaconfig._django import update_settings, DjangoSchema

# parse config file
parser = SchemaConfigParser(DjangoSchema())
parser.read(['test.cfg'])
update_settings(parser, locals())

# keep parser reference
__SCHEMACONFIGPARSER__ = parser

