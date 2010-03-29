from django.core.management.base import CommandError

from helpers import CommandTestCase, SchemaConfigCommandTestCase


class ValidateCommandTestCase(CommandTestCase):
    COMMAND = 'validate'

    def test_validate_non_schemaconfig_settings(self):
        self.call_command()
        expected_output = 'Settings appear to be fine'
        self.assertEqual(self.capture['stdout'].strip(), expected_output)


class ValidateSchemaConfigCommandTestCase(SchemaConfigCommandTestCase):
    COMMAND = 'validate'

    def test_valid_config(self):
        self.call_command()
        expected_output = 'Settings appear to be fine'
        self.assertEqual(self.capture['stdout'].strip(), expected_output)

    def test_invalid_config(self):
        config = """
[bogus]
invalid_setting = foo
"""
        self.set_config(config)
        self.assertRaises(SystemExit, self.call_command)

        try:
            self.call_command()
        except SystemExit, e:
            self.assertEqual(e.code, 1)
            self.assertEqual(self.capture['stderr'].strip(), 'Error: Settings did not validate against schema')


