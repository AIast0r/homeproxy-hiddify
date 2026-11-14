#!/usr/bin/env python3
"""Regression checks for the opt-in HWID subscription patch.

These are source-level tests, not a substitute for ucode execution
and an OpenWrt integration test with a real subscription provider.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (ROOT / "root/etc/homeproxy/scripts/update_subscriptions.uc").read_text()
VIEW = (ROOT / "htdocs/luci-static/resources/view/homeproxy/node.js").read_text()
BUILD = (ROOT / ".github/build-ipk.sh").read_text()
MAKEFILE = (ROOT / "Makefile").read_text()


class SubscriptionHWIDTests(unittest.TestCase):
    def test_opt_in_and_persisted_random_identity(self):
        self.assertIn("'send_hwid') === '1'", SCRIPT)
        self.assertIn("readfile('/proc/sys/kernel/random/uuid')", SCRIPT)
        self.assertIn("uci.set(uciconfig, ucisubscription, 'hwid', id)", SCRIPT)
        self.assertIn("uci.commit(uciconfig)", SCRIPT)
        self.assertIn("if (!send_hwid) return wGET(url, agent);", SCRIPT)

    def test_headers_and_safe_fetch(self):
        for header in ("X-HWID", "X-Device-OS", "X-Ver-OS", "X-Device-Model"):
            self.assertIn(header, SCRIPT)
        self.assertIn("--max-redirs 0", SCRIPT)
        self.assertIn("Invalid subscription device header", SCRIPT)
        self.assertIn("HWID subscription must use HTTPS", SCRIPT)
        self.assertIn("Invalid subscription device header", SCRIPT)
        self.assertIn("shellquote(url)", SCRIPT)
        self.assertNotIn("--location-trusted", SCRIPT)

    def test_all_subscription_paths_use_header_aware_fetcher(self):
        self.assertIn("let res = fetch_subscription(", SCRIPT)
        self.assertIn("res = fetch_subscription(url, user_agent)", SCRIPT)
        self.assertIn("const rawRes = fetch_subscription(rawUrl, user_agent)", SCRIPT)
        self.assertEqual(SCRIPT.count("wGET("), 2)  # comment and compatibility path

    def test_netshift_identity_generator_profiles(self):
        for app in ("Happ", "INCY"):
            self.assertIn(app + ": {", VIEW)
        for platform in ("Android:", "AndroidTV:", "iOS:", "macOS:", "Windows:", "'Mac OS X':", "'Windows 11':", "'Windows 10':"):
            self.assertIn(platform, VIEW)
        self.assertIn("function hpPickWeighted", VIEW)
        self.assertIn("function hpGenerateClient", VIEW)
        self.assertIn("o.onclick = function(ev, section_id)", VIEW)
        self.assertIn("widget.setValue(identity[key])", VIEW)
        self.assertIn("hpChars(HP_HEX, 16)", VIEW)
        self.assertIn("hpChars(HP_HEX, 32).toUpperCase()", VIEW)

    def test_ui_and_package_dependencies(self):
        for option in ("send_hwid", "hwid", "device_os", "device_os_version", "device_model"):
            self.assertIn("'" + option + "'", VIEW)
        self.assertIn("+curl", MAKEFILE)
        self.assertIn("ucode-mod-digest curl", BUILD)


if __name__ == "__main__":
    unittest.main()
