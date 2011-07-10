# Copyright 2010-2011 Canonical Ltd.  This software is licensed under the
# GNU Lesser General Public License version 3 (see the file LICENSE).
# Copyright 2009-2011 by Barry A. Warsaw

import re


DEFAULT_VERSION_RE = re.compile(r'(?P<version>\d+\.\d(?:\.\d+)?)')


def get_version(filename, pattern=None):
    """Extract the __version__ from a file without importing it.

    While you could get the __version__ by importing the module, the very act
    of importing can cause unintended consequences.  For example, Distribute's
    automatic 2to3 support will break.  Instead, this searches the file for a
    line that starts with __version__, and extract the version number by
    regular expression matching.

    By default, two or three dot-separated digits are recognized, but by
    passing a pattern parameter, you can recognize just about anything.  Use
    the `version` group name to specify the match group.

    :param filename: The name of the file to search.
    :type filename: string
    :param pattern: Optional alternative regular expression pattern to use.
    :type pattern: string
    :return: The version that was extracted.
    :rtype: string
    """
    if pattern is None:
        cre = DEFAULT_VERSION_RE
    else:
        cre = re.compile(pattern)
    with open(filename) as fp:
        for line in fp:
            if line.startswith('__version__'):
                mo = cre.search(line)
                assert mo, 'No valid __version__ string found'
                return mo.group('version')
    raise AssertionError('No __version__ assignment found')
