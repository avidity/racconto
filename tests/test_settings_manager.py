import unittest
import imp

from racconto.settings_manager import SettingsManager

class TestSettingsManager(unittest.TestCase):
    def setUp(self):
        self.manager = SettingsManager()

    def tearDown(self):
        del self.manager

    def test_initializes_settings(self):
        self.assertIsInstance(self.manager.settings, dict)

    def test_settings_contain_default_values(self):
        self.assertEqual(self.manager.settings['SITEDIR'], 'site')
        self.assertEqual(self.manager.settings['FILTERS'], {})

    def test_get_value(self):
        self.manager.settings['TEST_KEY'] = "woop"
        self.assertEquals(self.manager.get('TEST_KEY'), 'woop')

    def test_override(self):
        overrides = imp.new_module('override_module')
        implementation = "SITEDIR = '/another/path'"
        exec implementation in overrides.__dict__
        self.manager.override(overrides)
        self.assertEquals(self.manager.get('SITEDIR'), '/another/path')
        # Restore default settings
        self.manager.override(None)
