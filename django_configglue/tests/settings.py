# Copyright 2010 Canonical Ltd.  This software is licensed under the
# GNU Lesser General Public License version 3 (see the file LICENSE).

import django
from django_configglue.utils import configglue
from django_configglue.schema import schemas


DjangoSchema = schemas.get(django.get_version())
configglue(DjangoSchema, ['main.cfg', 'test.cfg'], __name__)

