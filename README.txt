= Running tests =

In order to run the tests for the django_settings app, go to the
test_django_settings folder, and run the django test suite from there.

As django_settings supports schemaconfig generate settings, if schemaconfig
and its dependencies is installed, the test suite will run those tests
covering schemaconfig support. Otherwise they will be left out.
