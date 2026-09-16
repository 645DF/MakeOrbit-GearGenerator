import json
import pathlib
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from makeorbit_bridge import MakeOrbitError, load_config


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


if __name__ == "__main__":
    unittest.main()
