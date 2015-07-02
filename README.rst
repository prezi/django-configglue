Overview
========

*consider this a fork of https://code.launchpad.net/django-configglue*
*this git repo has been converted from bzr, using the ``tailor`` tool - http://progetti.arstecnica.it/tailor - please excuse any apparent mishaps as a result, we'll clean up in time.*

django-configglue brings all the joy of ConfigGlue - http://configglue.readthedocs.org/en/latest/index.html - to your django project.


Running tests
=============

django_configglue is a normal django application, so running the tests
should be as easy as running ::

	cd testproject
	PYTHONPATH=.. python manage.py test django_configglue

As a shortcut, you can also run ::

	python setup.py test

.. note:: django-configglue has only been tested with Python 2.6 but should
	work on Python 2.4+.

You can also run the tests for different combinations of Python and Django
versions using tox ::

    tox -e py27-django17

Getting started
===============

For documentation on django-configglue, please refer to the files found under
the ``doc`` folder.


Support
=======

Feel free to submit bug reports, suggestions, etc as tickets in github: https://github.com/IDCubed/django-configglue/issues
