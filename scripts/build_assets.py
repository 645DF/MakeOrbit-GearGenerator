#!/usr/bin/env python3
"""Build toolbar icons and compact dimension tool-clips."""

import math
import pathlib
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from gear_core import GearRequest, calculate, outline

GREEN = "#5f8172"
DARK = "#17312a"
MID = "#9bb2a8"
PALE = "#eef3f0"
ORANGE = "#e68032"


def font(size, bold=False):
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for candidate in candidates:
        if pathlib.Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def gear_points(teeth=14, radius=88, cx=130, cy=130, squash=0.68, offset=(0, 0)):
    pts = []
    for i in range(teeth * 4):
        angle = 2 * math.pi * i / (teeth * 4)
        phase = i % 4
        r = radius if phase in (1, 2) else radius * 0.78
        x = cx + offset[0] + r * math.cos(angle)
        y = cy + offset[1] + r * math.sin(angle) * squash
        pts.append((x, y))
    return pts


def base_canvas(title, symbol):
    image = Image.new("RGB", (480, 300), "white")
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((8, 8, 472, 292), radius=18, fill=PALE, outline=MID, width=2)
    draw.text((280, 32), title, fill=DARK, font=font(24, True))
    draw.text((280, 72), symbol, fill=ORANGE, font=font(34, True))
    return image, draw


def draw_gear(draw, kind="external"):
    if kind == "internal":
        draw.ellipse((35, 45, 245, 215), fill=DARK)
        draw.polygon(gear_points(cx=140, cy=130, radius=72), fill="white")
        draw.ellipse((102, 101, 178, 159), outline=GREEN, width=4)
    elif kind == "sprocket":
        shadow = gear_points(teeth=12, radius=90, offset=(0, 14))
        draw.polygon(shadow, fill=DARK)
        draw.polygon(gear_points(teeth=12, radius=90), fill=GREEN, outline=DARK)
        draw.ellipse((105, 103, 155, 157), fill="white", outline=DARK, width=3)
        for i in range(12):
            a = i * 2 * math.pi / 12
            x, y = 130 + 68 * math.cos(a), 130 + 46 * math.sin(a)
            draw.ellipse((x - 7, y - 5, x + 7, y + 5), fill="white", outline=DARK)
    else:
        draw.polygon(gear_points(offset=(0, 14)), fill=DARK)
        draw.polygon(gear_points(), fill=GREEN, outline=DARK)
        draw.ellipse((98, 108, 162, 152), fill="white", outline=DARK, width=3)


def arrow(draw, start, end, label):
    draw.line((start, end), fill=ORANGE, width=4)
    angle = math.atan2(end[1] - start[1], end[0] - start[0])
    for point, reverse in ((start, 0), (end, math.pi)):
        a = angle + reverse
        wing1 = (point[0] - 13 * math.cos(a - .45), point[1] - 13 * math.sin(a - .45))
        wing2 = (point[0] - 13 * math.cos(a + .45), point[1] - 13 * math.sin(a + .45))
        draw.polygon((point, wing1, wing2), fill=ORANGE)
    box = draw.textbbox((0, 0), label, font=font(22, True))
    x = (start[0] + end[0] - (box[2] - box[0])) / 2
    y = (start[1] + end[1]) / 2 - 28
    draw.text((x, y), label, fill=ORANGE, font=font(22, True))


def save_clip(filename, title, symbol, kind="external", arrow_data=None):
    image, draw = base_canvas(title, symbol)
    draw_gear(draw, kind)
    if arrow_data:
        arrow(draw, *arrow_data)
    image.save(ROOT / "resources" / "toolclips" / filename, optimize=True)


def build():
    command = ROOT / "resources" / "command"
    clips = ROOT / "resources" / "toolclips"
    command.mkdir(parents=True, exist_ok=True); clips.mkdir(parents=True, exist_ok=True)
    for size in (16, 32, 64):
        image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        scale = size / 260
        pts = [(x * scale, y * scale) for x, y in gear_points(cx=130, cy=130, radius=112, squash=1)]
        draw.polygon(pts, fill=GREEN, outline=DARK)
        draw.ellipse((size*.34, size*.34, size*.66, size*.66), fill="white", outline=DARK, width=max(1, size//32))
        image.save(command / f"{size}x{size}.png")
    save_clip("types.png", "Gear type", "3 ×", "sprocket")
    save_clip("teeth.png", "Tooth count", "z", "external", ((50, 235), (222, 235), "z"))
    save_clip("component.png", "Component", "3D", "external")
    save_clip("pressure.png", "Pressure angle", "α", "external", ((145, 130), (225, 78), "α"))
    save_clip("backlash.png", "Backlash", "j", "external", ((196, 122), (223, 122), "j"))
    save_clip("bore.png", "Bore radius", "r", "external", ((130, 130), (160, 130), "r"))
    save_clip("module.png", "Module", "m=d/z", "external")
    save_clip("pitch.png", "Circular pitch", "p=πm", "external", ((155, 214), (205, 190), "p"))
    save_clip("diameters.png", "Reference circles", "d / da / df", "external", ((42, 130), (218, 130), "d"))
    save_clip("thickness.png", "Extrusion", "b", "external", ((52, 235), (130, 250), "b"))
    save_clip("internal.png", "Ring wall", "s", "internal", ((48, 128), (78, 128), "s"))
    save_clip("tip-radius.png", "Tooth-tip radius", "ra", "external", ((130, 130), (205, 100), "ra"))
    save_clip("root-radius.png", "Tooth-root radius", "rf", "external", ((130, 130), (192, 130), "rf"))
    save_clip("chain-pitch.png", "Chain pitch", "p", "sprocket", ((75, 225), (150, 238), "p"))
    save_clip("chain-width.png", "Chain width", "bi", "sprocket", ((80, 235), (185, 235), "bi"))
    save_clip("roller.png", "Roller seat", "R=(dr/2)+c", "sprocket", ((150, 130), (205, 130), "R"))
    save_clip("connector.png", "Connector wall", "s", "sprocket", ((75, 235), (115, 242), "s"))


if __name__ == "__main__":
    build()
