import os.path

from django.conf import settings, global_settings

from helpers import CommandTestCase, SchemaConfigCommandTestCase

try:
    import schemaconfig
    __SCHEMACONFIG__ = True
except ImportError:
    __SCHEMACONFIG__ = False


class DjangoSettingsCommandTestCase(CommandTestCase):
    COMMAND = 'settings'

    def test_no_args(self):
        self.call_command()
        self.assertTrue(self.capture['stdout'].startswith('Usage: '))

    def test_get(self):
        self.call_command('installed_apps')
        expected_output = "INSTALLED_APPS = ['django_settings']"
        self.assertEqual(self.capture['stdout'].strip(), expected_output)

    def test_get_not_found(self):
        self.call_command('bogus')
        expected_output = "setting BOGUS not found"
        self.assertEqual(self.capture['stdout'].strip(), expected_output)

    def test_show(self):
        self.call_command(show_current=True)
        expected_output = "SETTINGS_MODULE = 'test_django_settings.settings'"
        self.assertEqual(self.capture['stdout'].strip(), expected_output)

    def test_show_global(self):
        self.call_command(show_current=True, include_global=True)
        expected_output = dict([(key, getattr(settings, key)) for key in
            settings.get_all_members() if key.isupper()])
        # process output into dictionary
        items = map(lambda x: x.split(' = '), self.capture['stdout'].strip().split('\n'))
        items = map(lambda x: (x[0].strip(), eval(x[1].strip())), items)
        output = dict(items)
        # test equality
        self.assertEqual(output, expected_output)

    def test_locate_django_setting(self):
        self.call_command('installed_apps', locate=True)
        mod = __import__(settings.SETTINGS_MODULE, globals(), locals(), [''])
        location = os.path.abspath(mod.__file__)
        expected_output = "setting INSTALLED_APPS last defined in '%s'" % \
            location
        self.assertEqual(self.capture['stdout'].strip(), expected_output)

    def test_locate_django_setting_not_found(self):
        self.call_command('bogus', locate=True)
        expected_output = "setting BOGUS not found"
        self.assertEqual(self.capture['stdout'].strip(), expected_output)


class ValidateCommandTestCase(CommandTestCase):
    COMMAND = 'settings'

    def test_validate_non_schemaconfig_settings(self):
        self.call_command(validate=True)
        expected_output = 'Settings appear to be fine'
        self.assertEqual(self.capture['stdout'].strip(), expected_output)


if __SCHEMACONFIG__:
    class SchemaConfigSettingsCommandTestCase(SchemaConfigCommandTestCase):
        COMMAND = 'settings'

        def test_locate_schemaconfig_setting(self):
            self.call_command('installed_apps', locate=True)
            location = os.path.join(os.path.abspath(os.path.curdir), 'test.cfg')
            expected_output = "setting INSTALLED_APPS last defined in '%s'" % \
                location
            self.assertEqual(self.capture['stdout'].strip(), expected_output)

        def test_locate_schemaconfig_setting_not_found(self):
            self.call_command('bogus', locate=True)
            expected_output = 'setting BOGUS not found'
            self.assertEqual(self.capture['stdout'].strip(), expected_output)


    class ValidateSchemaConfigCommandTestCase(SchemaConfigCommandTestCase):
        COMMAND = 'settings'

        def test_valid_config(self):
            self.call_command(validate=True)
            expected_output = 'Settings appear to be fine'
            self.assertEqual(self.capture['stdout'].strip(), expected_output)

        def test_invalid_config(self):
            config = """
[bogus]
invalid_setting = foo
"""
            self.set_config(config)
            self.assertRaises(SystemExit, self.call_command, validate=True)

            try:
                self.call_command(validate=True)
            except SystemExit, e:
                self.assertEqual(e.code, 1)
                error_msg = 'Error: Settings did not validate against schema'
                self.assertTrue(self.capture['stderr'].strip().startswith(
                    error_msg))


