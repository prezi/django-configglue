# Copyright 2010-2011 Canonical Ltd.  This software is licensed under the
# GNU Lesser General Public License version 3 (see the file LICENSE).

import django
from django_configglue.utils import configglue
from django_configglue.schema import schemas


DjangoSchema = schemas.get(django.get_version(), strict=False)

version = DjangoSchema.version
main_cfg = 'main.cfg'
if version >= '1.5':
    main_cfg = 'main-15.cfg'
elif version >= '1.4':
    main_cfg = 'main-14.cfg'
elif version >= '1.3':
    main_cfg = 'main-13.cfg'
elif version >= '1.2':
    main_cfg = 'main-12.cfg'

configglue(DjangoSchema, [main_cfg, 'test.cfg'], __name__)
