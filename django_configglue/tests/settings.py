# Copyright 2010 Canonical Ltd.  This software is licensed under the
# GNU Lesser General Public License version 3 (see the file LICENSE).

import django
from configglue.pyschema import SchemaConfigParser
from django_configglue.utils import update_settings
from django_configglue.schema import schemas


DjangoSchema = schemas.get(django.get_version())
# parse config file
parser = SchemaConfigParser(DjangoSchema())
parser.read(['main.cfg', 'test.cfg'])
update_settings(parser, locals())

# keep parser reference
__CONFIGGLUE_PARSER__ = parser

