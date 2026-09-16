import json
import pathlib
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from makeorbit_bridge import MAKEORBIT_BETA_URL, MakeOrbitError, load_config, unavailable_guidance


class BridgeTests(unittest.TestCase):
    def test_rejects_non_loopback_configuration(self):
        with tempfile.TemporaryDirectory() as folder:
            addin = pathlib.Path(folder) / "MakeOrbitGearGenerator"
            config_dir = pathlib.Path(folder) / "MakeOrbitFusion"
            addin.mkdir(); config_dir.mkdir()
            (config_dir / "bridge_config.json").write_text(
                json.dumps({"host": "example.com", "port": 64536, "token": "secret"}), encoding="utf-8"
            )
            with patch("makeorbit_bridge.config_candidates", return_value=[config_dir / "bridge_config.json"]):
                with self.assertRaises(MakeOrbitError):
                    load_config(addin)

    def test_accepts_sibling_makeorbit_configuration(self):
        with tempfile.TemporaryDirectory() as folder:
            addin = pathlib.Path(folder) / "MakeOrbitGearGenerator"
            config_dir = pathlib.Path(folder) / "MakeOrbitFusion"
            addin.mkdir(); config_dir.mkdir()
            expected = {"host": "127.0.0.1", "port": 64536, "token": "secret"}
            (config_dir / "bridge_config.json").write_text(json.dumps(expected), encoding="utf-8")
            with patch("makeorbit_bridge.config_candidates", return_value=[config_dir / "bridge_config.json"]):
                self.assertEqual(load_config(addin), expected)

    def test_macos_guidance_links_to_beta_page(self):
        message, url = unavailable_guidance("Darwin", True)
        self.assertIn("macOS-Betatest", message)
        self.assertEqual(url, MAKEORBIT_BETA_URL)

    def test_windows_guidance_announces_planned_version_without_link(self):
        message, url = unavailable_guidance("Windows", False)
        self.assertIn("Windows version", message)
        self.assertIn("planned", message)
        self.assertIsNone(url)


if __name__ == "__main__":
    unittest.main()
