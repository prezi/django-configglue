import os.path
import sys
from StringIO import StringIO

from django.conf import settings, global_settings
from django.core import management
from django.test import TestCase

try:
    import schemaconfig
    __SCHEMACONFIG__ = True
except ImportError:
    __SCHEMACONFIG__ = False


class SettingsCommandTestCase(TestCase):
    def begin_capture(self):
        self._stdout = sys.stdout
        self._stderr = sys.stderr
        sys.stdout = StringIO()
        sys.stderr = StringIO()

    def end_capture(self):
        sys.stdout = self._stdout
        sys.stderr = self._stderr

    def call_command(self, *args, **kwargs):
        self.begin_capture()

        management.call_command('settings', *args, **kwargs)
        sys.stdout.seek(0)
        output = sys.stdout.read()

        self.end_capture()

        return output


class DjangoSettingsCommandTestCase(SettingsCommandTestCase):
    def test_no_args(self):
        output = self.call_command()
        self.assertTrue(output.startswith('Usage: '))

    def test_get(self):
        output = self.call_command('installed_apps')
        expected_output = "INSTALLED_APPS = ['django_settings']"
        self.assertEqual(output.strip(), expected_output)

    def test_get_not_found(self):
        output = self.call_command('bogus')
        expected_output = "setting BOGUS not found"
        self.assertEqual(output.strip(), expected_output)

    def test_show(self):
        output = self.call_command(show_current=True)
        expected_output = "SETTINGS_MODULE = 'test_django_settings.settings'"
        self.assertEqual(output.strip(), expected_output)

    def test_show_global(self):
        output = self.call_command(show_current=True, include_global=True)
        expected_output = dict([(key, getattr(settings, key)) for key in
            settings.get_all_members() if key.isupper()])
        # process output into dictionary
        items = map(lambda x: x.split(' = '), output.strip().split('\n'))
        items = map(lambda x: (x[0].strip(), eval(x[1].strip())), items)
        output = dict(items)
        # test equality
        self.assertEqual(output, expected_output)

    def test_locate_django_setting(self):
        output = self.call_command('installed_apps', locate=True)
        mod = __import__(settings.SETTINGS_MODULE, globals(), locals(), [''])
        location = os.path.abspath(mod.__file__)
        expected_output = "setting INSTALLED_APPS last defined in '%s'" % \
            location
        self.assertEqual(output.strip(), expected_output)

    def test_locate_django_setting_not_found(self):
        output = self.call_command('bogus', locate=True)
        expected_output = "setting BOGUS not found"
        self.assertEqual(output.strip(), expected_output)


if __SCHEMACONFIG__:
    class SchemaConfigSettingsCommandTestCase(SettingsCommandTestCase):
        def setUp(self):
            config = open('test.cfg', 'w')
            config.writelines(['[django]\n', 'installed_apps = django_settings'])
            config.close()

            self.load_schemaconfig_settings()

        def tearDown(self):
            self.unload_schemaconfig_settings()

            os.remove('test.cfg')

        def load_schemaconfig_settings(self):
            self._DJANGO_SETTINGS_MODULE = os.environ['DJANGO_SETTINGS_MODULE']
            self._SETTINGS_MODULE = settings.SETTINGS_MODULE
            os.environ['DJANGO_SETTINGS_MODULE'] = 'test_django_settings.settings_schemaconfig'
            settings.SETTINGS_MODULE = 'test_django_settings.settings_schemaconfig'

            mod = __import__(settings.SETTINGS_MODULE, globals(), locals(), [''])
            atts = vars(mod)
            for att in atts:
                setattr(settings, att, getattr(mod, att))

        def unload_schemaconfig_settings(self):
            settings.SETTINGS_MODULE = self._SETTINGS_MODULE
            os.environ['DJANGO_SETTINGS_MODULE'] = self._DJANGO_SETTINGS_MODULE

        def test_locate_schemaconfig_setting(self):
            output = self.call_command('installed_apps', locate=True)
            location = os.path.join(os.path.abspath(os.curdir), 'test.cfg')
            expected_output = "setting INSTALLED_APPS last defined in '%s'" % \
                location
            self.assertEqual(output.strip(), expected_output)

        def test_locate_schemaconfig_setting_not_found(self):
            output = self.call_command('bogus', locate=True)
            expected_output = 'setting BOGUS not found'
            self.assertEqual(output.strip(), expected_output)
