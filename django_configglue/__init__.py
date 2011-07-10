# Copyright 2010 Canonical Ltd.  This software is licensed under the
# GNU Lesser General Public License version 3 (see the file LICENSE).

__version__ = '0.5'

# monkey-patch django's management utility
from . import management
