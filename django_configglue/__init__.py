# Copyright 2010-2011 Canonical Ltd.  This software is licensed under the
# GNU Lesser General Public License version 3 (see the file LICENSE).

__version__ = '0.6.1'

# monkey-patch django's management utility
from . import management
