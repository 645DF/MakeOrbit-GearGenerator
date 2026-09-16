"""Pure-Python gear calculations used by the Fusion add-in and unit tests.

All public dimensions are millimetres.  No Autodesk modules are imported here,
which keeps the sizing and validation logic testable outside Fusion.
"""

from dataclasses import dataclass, asdict
import math


class GearError(ValueError):
    pass


@dataclass
class GearRequest:
    kind: str = "external"  # external, internal, sprocket
    teeth: int = 20
    module: float | None = None
    circular_pitch: float | None = None
    pitch_diameter: float | None = None
    outside_diameter: float | None = None
    root_diameter: float | None = None
    pressure_angle_deg: float = 20.0
    backlash: float = 0.05
    thickness: float | None = None
    bore_radius: float | None = None
    ring_wall: float | None = None
    tip_radius: float | None = None
    root_radius: float | None = None
    chain_link_length: float | None = None
    chain_link_width: float | None = None
    roller_diameter: float | None = None
    roller_thickness: float | None = None
    connector_wall: float | None = None
    roller_clearance: float = 0.15


@dataclass
class GearResult:
    kind: str
    teeth: int
    module: float
    circular_pitch: float
    pitch_radius: float
    pitch_diameter: float
    outside_radius: float
    outside_diameter: float
    root_radius: float
    root_diameter: float
    tip_circle_radius: float
    base_radius: float
    thickness: float
    bore_radius: float | None
    pressure_angle_deg: float
    backlash: float
    tip_round_radius: float
    root_round_radius: float
    roller_seat_radius: float | None = None
    chain_pitch: float | None = None
    chain_link_width: float | None = None
    roller_diameter: float | None = None
    roller_thickness: float | None = None
    connector_wall: float | None = None

    def as_dict(self):
        return asdict(self)


def _positive(name, value, allow_zero=False):
    if value is None:
        return
    if value < 0 or (value == 0 and not allow_zero):
        raise GearError(f"{name} must be positive")


def _choose_module(req: GearRequest) -> float:
    candidates = []
    if req.module is not None:
        candidates.append(("module", req.module))
    if req.circular_pitch is not None:
        candidates.append(("circular pitch", req.circular_pitch / math.pi))
    if req.pitch_diameter is not None:
        candidates.append(("pitch diameter", req.pitch_diameter / req.teeth))
    if req.kind == "external" and req.outside_diameter is not None:
        candidates.append(("outside diameter", req.outside_diameter / (req.teeth + 2.0)))
    if req.kind == "external" and req.tip_radius is not None:
        candidates.append(("tooth-tip radius", req.tip_radius / (req.teeth / 2.0 + 1.0)))
    if req.kind == "external" and req.root_diameter is not None and req.teeth > 2.5:
        candidates.append(("root diameter", req.root_diameter / (req.teeth - 2.5)))
    if req.kind == "external" and req.root_radius is not None and req.teeth > 2.5:
        candidates.append(("tooth-root radius", req.root_radius / (req.teeth / 2.0 - 1.25)))
    if req.kind == "internal" and req.tip_radius is not None and req.teeth > 2:
        candidates.append(("tooth-tip radius", req.tip_radius / (req.teeth / 2.0 - 1.0)))
    if req.kind == "internal" and req.root_diameter is not None:
        candidates.append(("root diameter", req.root_diameter / (req.teeth + 2.5)))
    if req.kind == "internal" and req.root_radius is not None:
        candidates.append(("tooth-root radius", req.root_radius / (req.teeth / 2.0 + 1.25)))
    if not candidates:
        return 2.0
    for label, value in candidates:
        _positive(label, value)
    selected = candidates[0][1]
    for label, value in candidates[1:]:
        if abs(value - selected) / selected > 0.02:
            raise GearError(
                f"Conflicting size inputs: {candidates[0][0]} implies module "
                f"{selected:.4g} mm, while {label} implies {value:.4g} mm"
            )
    return sum(value for _, value in candidates) / len(candidates)


def calculate(req: GearRequest) -> GearResult:
    if req.kind not in {"external", "internal", "sprocket"}:
        raise GearError("Unsupported gear type")
    if not isinstance(req.teeth, int) or req.teeth < (6 if req.kind == "sprocket" else 8):
        raise GearError("Tooth count is required and too small for the selected type")
    for name in (
        "module", "circular_pitch", "pitch_diameter", "outside_diameter",
        "root_diameter", "thickness", "ring_wall", "tip_radius", "root_radius",
        "chain_link_length", "chain_link_width", "roller_diameter",
        "roller_thickness", "connector_wall",
    ):
        _positive(name.replace("_", " "), getattr(req, name))
    _positive("roller clearance", req.roller_clearance, allow_zero=True)
    _positive("backlash", req.backlash, allow_zero=True)
    if not 5 <= req.pressure_angle_deg <= 35:
        raise GearError("Pressure angle must be between 5 and 35 degrees")

    if req.kind == "sprocket":
        pitch = req.chain_link_length or req.circular_pitch or 12.7
        roller_diameter = req.roller_diameter or pitch * 0.61
        roller_thickness = req.roller_thickness or req.chain_link_width or pitch * 0.26
        link_width = req.chain_link_width or roller_thickness
        wall = req.connector_wall
        available = min(link_width, roller_thickness)
        if wall is not None:
            available -= 2.0 * wall
        thickness = req.thickness or available
        if thickness <= 0:
            raise GearError("Connector wall thickness leaves no room for the sprocket")
        pitch_radius = pitch / (2.0 * math.sin(math.pi / req.teeth))
        seat_radius = roller_diameter / 2.0 + req.roller_clearance
        root_radius = req.root_radius or (pitch_radius - seat_radius)
        outside_radius = (req.tip_radius if req.tip_radius else req.outside_diameter / 2.0 if req.outside_diameter else
                          pitch * (0.6 + 1.0 / math.tan(math.pi / req.teeth)) / 2.0)
        if outside_radius <= root_radius:
            raise GearError("Outside radius must be larger than the roller-seat root radius")
        if req.bore_radius is not None and req.bore_radius >= root_radius:
            raise GearError("Bore radius must be smaller than the sprocket root radius")
        return GearResult(
            kind=req.kind, teeth=req.teeth, module=pitch / math.pi,
            circular_pitch=pitch, pitch_radius=pitch_radius,
            pitch_diameter=2 * pitch_radius, outside_radius=outside_radius,
            outside_diameter=2 * outside_radius, root_radius=root_radius,
            root_diameter=2 * root_radius, tip_circle_radius=outside_radius, base_radius=pitch_radius,
            thickness=thickness, bore_radius=req.bore_radius,
            pressure_angle_deg=req.pressure_angle_deg, backlash=req.backlash,
            tip_round_radius=max(0.2, pitch * 0.10),
            root_round_radius=seat_radius, roller_seat_radius=seat_radius,
            chain_pitch=pitch, chain_link_width=link_width,
            roller_diameter=roller_diameter, roller_thickness=roller_thickness,
            connector_wall=wall,
        )

    module = _choose_module(req)
    pitch_radius = module * req.teeth / 2.0
    pressure = math.radians(req.pressure_angle_deg)
    base_radius = pitch_radius * math.cos(pressure)
    if req.kind == "external":
        outside_radius = (req.tip_radius if req.tip_radius else req.outside_diameter / 2.0 if req.outside_diameter else pitch_radius + module)
        root_radius = (req.root_radius if req.root_radius else req.root_diameter / 2.0 if req.root_diameter else max(module * 0.8, pitch_radius - 1.25 * module))
        tip_circle_radius = outside_radius
        ring_wall = None
    else:
        tooth_tip = req.tip_radius or (pitch_radius - module)
        tooth_root = req.root_radius or (req.root_diameter / 2.0 if req.root_diameter else pitch_radius + 1.25 * module)
        root_radius = tooth_root
        tip_circle_radius = tooth_tip
        ring_wall = req.ring_wall or max(2.0 * module, 3.0)
        outside_radius = req.outside_diameter / 2.0 if req.outside_diameter else tooth_root + ring_wall
        if outside_radius <= tooth_root:
            raise GearError("Internal gear outside radius must include the tooth root and ring wall")
    if req.bore_radius is not None and req.kind == "external" and req.bore_radius >= root_radius:
        raise GearError("Bore radius must be smaller than the root radius")
    return GearResult(
        kind=req.kind, teeth=req.teeth, module=module,
        circular_pitch=math.pi * module, pitch_radius=pitch_radius,
        pitch_diameter=2 * pitch_radius, outside_radius=outside_radius,
        outside_diameter=2 * outside_radius, root_radius=root_radius,
        root_diameter=2 * root_radius, tip_circle_radius=tip_circle_radius, base_radius=base_radius,
        thickness=req.thickness or 5.0, bore_radius=req.bore_radius,
        pressure_angle_deg=req.pressure_angle_deg, backlash=req.backlash,
        tip_round_radius=max(0.12 * module, 0.05),
        root_round_radius=max(0.30 * module, 0.10),
    )


def _polar(radius, angle):
    return (radius * math.cos(angle), radius * math.sin(angle))


def _arc_points(radius, start, end, count):
    return [_polar(radius, start + (end - start) * i / count) for i in range(count)]


def _involute_angle(base_radius, radius):
    if radius <= base_radius:
        return 0.0
    alpha = math.acos(base_radius / radius)
    return math.tan(alpha) - alpha


def external_outline(result: GearResult, flank_steps=6, arc_steps=4):
    """Returns a closed, counter-clockwise involute gear outline."""
    z = result.teeth
    pitch = 2.0 * math.pi / z
    rp, rb, ra, rr = result.pitch_radius, result.base_radius, result.outside_radius, result.root_radius
    if not (0 < rr < ra):
        raise GearError("Invalid external radii")
    start_r = max(rb, rr)
    inv_pitch = _involute_angle(rb, rp)
    half_tooth = math.pi / (2.0 * z) - result.backlash / max(4.0 * rp, 1e-9)
    base_angle = half_tooth + inv_pitch - _involute_angle(rb, start_r)
    tip_angle = half_tooth + inv_pitch - _involute_angle(rb, ra)
    if tip_angle <= 0 or base_angle >= pitch / 2.0:
        raise GearError("Tooth geometry is not feasible; reduce backlash or change tooth count/module")
    points = []
    for tooth in range(z):
        center = tooth * pitch
        valley_before = center - pitch / 2.0
        points.extend(_arc_points(rr, valley_before, center - base_angle, arc_steps))
        if start_r > rr:
            points.append(_polar(start_r, center - base_angle))
        for i in range(flank_steps + 1):
            radius = start_r + (ra - start_r) * i / flank_steps
            angle = half_tooth + inv_pitch - _involute_angle(rb, radius)
            points.append(_polar(radius, center - angle))
        points.extend(_arc_points(ra, center - tip_angle, center + tip_angle, arc_steps)[1:])
        for i in range(flank_steps, -1, -1):
            radius = start_r + (ra - start_r) * i / flank_steps
            angle = half_tooth + inv_pitch - _involute_angle(rb, radius)
            points.append(_polar(radius, center + angle))
        if start_r > rr:
            points.append(_polar(rr, center + base_angle))
        points.extend(_arc_points(rr, center + base_angle, center + pitch / 2.0, arc_steps)[1:])
    return _dedupe(points)


def internal_outline(result: GearResult, flank_steps=6, arc_steps=4):
    """Returns the inner boundary of an internal involute gear.

    The conjugate outline is constructed by reflecting the standard external
    radial profile about the pitch circle. This preserves pitch and pressure
    angle while placing addendum toward the centre.
    """
    m, rp = result.module, result.pitch_radius
    virtual = GearResult(**{**result.as_dict(), "kind": "external",
                            "outside_radius": rp + m,
                            "outside_diameter": 2 * (rp + m),
                            "root_radius": max(m * 0.8, rp - 1.25 * m),
                            "root_diameter": 2 * max(m * 0.8, rp - 1.25 * m)})
    outline = external_outline(virtual, flank_steps, arc_steps)
    converted = []
    for x, y in outline:
        radius = math.hypot(x, y)
        angle = math.atan2(y, x)
        converted_radius = 2.0 * rp - radius
        default_tip, default_root = rp - m, rp + 1.25 * m
        if converted_radius <= rp:
            scale = (rp - result.tip_circle_radius) / max(rp - default_tip, 1e-9)
            converted_radius = rp - (rp - converted_radius) * scale
        else:
            scale = (result.root_radius - rp) / max(default_root - rp, 1e-9)
            converted_radius = rp + (converted_radius - rp) * scale
        converted.append(_polar(converted_radius, angle))
    return _dedupe(converted)


def sprocket_outline(result: GearResult, pocket_steps=8, crown_steps=14):
    """Returns a sprocket outline with true circular roller-seat pockets."""
    z = result.teeth
    angular_pitch = 2.0 * math.pi / z
    rp = result.pitch_radius
    seat = result.roller_seat_radius
    if seat is None or seat >= rp:
        raise GearError("Roller seat is too large for the selected tooth count")
    pocket_half = min(angular_pitch * 0.28, math.asin(seat / rp) * 0.88)
    points = []
    for gap in range(z):
        center = gap * angular_pitch
        for i in range(pocket_steps + 1):
            offset = -pocket_half + 2.0 * pocket_half * i / pocket_steps
            under = seat * seat - rp * rp * math.sin(offset) ** 2
            radius = rp * math.cos(offset) - math.sqrt(max(0.0, under))
            points.append(_polar(radius, center + offset))
        start = center + pocket_half
        end = center + angular_pitch - pocket_half
        r0 = math.hypot(*points[-1])
        for i in range(1, crown_steps + 1):
            u = i / crown_steps
            raised = math.sin(math.pi * u) ** 0.72
            radius = r0 + (result.outside_radius - r0) * raised
            points.append(_polar(radius, start + (end - start) * u))
    return _dedupe(points)


def outline(result: GearResult):
    if result.kind == "external":
        return external_outline(result)
    if result.kind == "internal":
        return internal_outline(result)
    return sprocket_outline(result)


def _dedupe(points, tolerance=1e-7):
    cleaned = []
    for point in points:
        if not cleaned or math.dist(cleaned[-1], point) > tolerance:
            cleaned.append(point)
    if len(cleaned) < 3:
        raise GearError("Generated outline contains too few points")
    return cleaned
