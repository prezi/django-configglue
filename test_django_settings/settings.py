# minimal settings for testing django_settings

DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = 'test_django_settings.db'

INSTALLED_APPS = (
    'django_settings',
)

# if django-test-coverage is installed this test runner can be used to get
# test coverage report
#TEST_RUNNER = 'django-test-coverage.runner.run_tests'

