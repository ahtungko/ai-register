import importlib
import tempfile
import unittest
from pathlib import Path

from register.grok import grok


class FakeBrowser:
    def __init__(self):
        self.quit_called = False

    def quit(self):
        self.quit_called = True


class FakeDisplay:
    def __init__(self):
        self.stop_called = False

    def stop(self):
        self.stop_called = True


class StopBrowserXvfbCleanupTests(unittest.TestCase):
    def setUp(self):
        importlib.reload(grok)

    def tearDown(self):
        grok._set_browser(None)
        grok._set_page(None)
        grok._set_chrome_temp_dir("")
        grok._virtual_display = None
        grok._active_browser_count = 0

    def test_stop_browser_stops_xvfb_when_last_browser_exits(self):
        browser = FakeBrowser()
        display = FakeDisplay()
        grok._set_browser(browser)
        grok._virtual_display = display
        grok._active_browser_count = 1

        temp_dir = tempfile.mkdtemp(prefix="xvfb_cleanup_test_")
        grok._set_chrome_temp_dir(temp_dir)

        grok.stop_browser()

        self.assertTrue(browser.quit_called)
        self.assertTrue(display.stop_called)
        self.assertIsNone(grok._virtual_display)
        self.assertEqual(grok._active_browser_count, 0)
        self.assertFalse(Path(temp_dir).exists())

    def test_stop_browser_keeps_xvfb_when_other_browsers_are_active(self):
        browser = FakeBrowser()
        display = FakeDisplay()
        grok._set_browser(browser)
        grok._virtual_display = display
        grok._active_browser_count = 2

        grok.stop_browser()

        self.assertTrue(browser.quit_called)
        self.assertFalse(display.stop_called)
        self.assertIs(grok._virtual_display, display)
        self.assertEqual(grok._active_browser_count, 1)


if __name__ == "__main__":
    unittest.main()
