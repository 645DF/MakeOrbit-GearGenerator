import json
import math
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from gear_core import GearError, GearRequest, calculate, outline


class GearCalculationTests(unittest.TestCase):
    def test_tooth_count_is_required(self):
        with self.assertRaises(GearError):
            calculate(GearRequest(teeth=0))

    def test_default_external_uses_standard_module(self):
        value = calculate(GearRequest(teeth=20))
        self.assertAlmostEqual(value.module, 2.0)
        self.assertAlmostEqual(value.pitch_diameter, 40.0)
        self.assertAlmostEqual(value.outside_diameter, 44.0)
        self.assertIsNone(value.bore_radius)

    def test_module_can_be_derived_from_each_supported_dimension(self):
        cases = [
            GearRequest(teeth=20, circular_pitch=math.pi * 2),
            GearRequest(teeth=20, pitch_diameter=40),
            GearRequest(teeth=20, outside_diameter=44),
            GearRequest(teeth=20, root_diameter=35),
        ]
        for request in cases:
            with self.subTest(request=request):
                self.assertAlmostEqual(calculate(request).module, 2.0, places=6)

    def test_conflicting_dimensions_are_rejected(self):
        with self.assertRaisesRegex(GearError, "Conflicting"):
            calculate(GearRequest(teeth=20, module=2, pitch_diameter=60))

    def test_reference_drawing_tip_and_root_radii_are_supported(self):
        value = calculate(GearRequest(teeth=20, tip_radius=22.0, root_radius=17.5))
        self.assertAlmostEqual(value.outside_radius, 22.0)
        self.assertAlmostEqual(value.root_radius, 17.5)

    def test_internal_tip_and_root_radii_are_supported(self):
        value = calculate(GearRequest(kind="internal", teeth=40, tip_radius=38.0, root_radius=42.5))
        self.assertAlmostEqual(value.tip_circle_radius, 38.0)
        self.assertAlmostEqual(value.root_radius, 42.5)

    def test_optional_bore_must_fit(self):
        self.assertIsNone(calculate(GearRequest(teeth=20)).bore_radius)
        with self.assertRaises(GearError):
            calculate(GearRequest(teeth=20, bore_radius=18))

    def test_internal_gear_has_outer_ring(self):
        value = calculate(GearRequest(kind="internal", teeth=42, module=1.5, ring_wall=4))
        self.assertGreater(value.outside_radius, value.pitch_radius + 1.25 * value.module)
        self.assertGreater(len(outline(value)), 42 * 10)

    def test_sprocket_uses_chain_pitch_and_roller_radius(self):
        value = calculate(GearRequest(
            kind="sprocket", teeth=18, chain_link_length=12.7,
            chain_link_width=3.55, roller_diameter=7.75,
            roller_thickness=3.30, connector_wall=0.25,
        ))
        self.assertAlmostEqual(value.chain_pitch, 12.7)
        self.assertAlmostEqual(value.roller_seat_radius, 4.025)
        self.assertAlmostEqual(value.thickness, 2.8)
        self.assertGreater(len(outline(value)), 18 * 10)

    def test_all_outlines_are_finite_and_non_duplicate(self):
        values = [
            calculate(GearRequest(kind="external", teeth=16, module=1.5)),
            calculate(GearRequest(kind="internal", teeth=36, module=1.5)),
            calculate(GearRequest(kind="sprocket", teeth=14)),
        ]
        for value in values:
            points = outline(value)
            self.assertGreater(len(points), 100)
            self.assertTrue(all(math.isfinite(x) and math.isfinite(y) for x, y in points))
            self.assertTrue(all(points[i] != points[i - 1] for i in range(1, len(points))))
            json.dumps(value.as_dict())


if __name__ == "__main__":
    unittest.main()
