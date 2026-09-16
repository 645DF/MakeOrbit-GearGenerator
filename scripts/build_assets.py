#!/usr/bin/env python3
"""Build toolbar icons and bilingual technical dimension tool-clips."""

import math
import pathlib

from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parents[1]
GREEN = "#5f8172"
DARK = "#17312a"
MID = "#8fa89d"
PALE = "#eef3f0"
ORANGE = "#e68032"
BLUE = "#367fa3"
GREY = "#d7dfdb"


def font(size, bold=False):
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for candidate in candidates:
        if pathlib.Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def gear_points(teeth=14, radius=128, cx=190, cy=200, squash=1.0):
    pts = []
    for i in range(teeth * 4):
        angle = 2 * math.pi * i / (teeth * 4)
        r = radius if i % 4 in (1, 2) else radius * 0.79
        pts.append((cx + r * math.cos(angle), cy + r * math.sin(angle) * squash))
    return pts


def dashed_ellipse(draw, box, color, width=2, dash=14):
    for start in range(0, 360, dash * 2):
        draw.arc(box, start, start + dash, fill=color, width=width)


def arrow_head(draw, point, angle, color=ORANGE, size=11):
    p1 = (point[0] - size * math.cos(angle - 0.45), point[1] - size * math.sin(angle - 0.45))
    p2 = (point[0] - size * math.cos(angle + 0.45), point[1] - size * math.sin(angle + 0.45))
    draw.polygon((point, p1, p2), fill=color)


def dimension(draw, start, end, label, color=ORANGE, extensions=None):
    draw.line((start, end), fill=color, width=4)
    angle = math.atan2(end[1] - start[1], end[0] - start[0])
    arrow_head(draw, start, angle + math.pi, color)
    arrow_head(draw, end, angle, color)
    if extensions:
        for a, b in extensions:
            draw.line((a, b), fill=color, width=2)
    box = draw.textbbox((0, 0), label, font=font(22, True))
    x = (start[0] + end[0] - (box[2] - box[0])) / 2
    y = (start[1] + end[1]) / 2 - 30
    draw.rounded_rectangle((x - 5, y - 2, x + box[2] - box[0] + 5, y + 26), 5, fill="white")
    draw.text((x, y), label, fill=color, font=font(22, True))


def canvas(title, subtitle):
    image = Image.new("RGB", (640, 420), "white")
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((6, 6, 634, 414), radius=18, fill=PALE, outline=MID, width=2)
    draw.text((365, 28), title, fill=DARK, font=font(28, True))
    draw.multiline_text((365, 70), subtitle, fill=DARK, font=font(18), spacing=5)
    return image, draw


def front_gear(draw, kind="external", bore=True, reference=True):
    if kind == "internal":
        draw.ellipse((55, 65, 325, 335), fill=DARK, outline=DARK, width=3)
        draw.polygon(gear_points(teeth=16, radius=102), fill="white")
        draw.ellipse((127, 137, 253, 263), fill="white", outline=GREEN, width=4)
    else:
        pts = gear_points(teeth=14 if kind == "external" else 12)
        draw.polygon([(x + 8, y + 10) for x, y in pts], fill=DARK)
        draw.polygon(pts, fill=GREEN, outline=DARK)
        if bore:
            draw.ellipse((158, 168, 222, 232), fill="white", outline=DARK, width=3)
        if kind == "sprocket":
            for i in range(12):
                a = i * 2 * math.pi / 12
                x, y = 190 + 99 * math.cos(a), 200 + 99 * math.sin(a)
                draw.ellipse((x - 10, y - 10, x + 10, y + 10), fill="white", outline=DARK, width=2)
    if reference:
        dashed_ellipse(draw, (78, 88, 302, 312), BLUE, 2)
        draw.line((190, 200, 190, 78), fill=MID, width=2)
        draw.ellipse((186, 196, 194, 204), fill=ORANGE)


def side_view(draw, x=385, y=205, width=190, thickness=48, inner=False):
    draw.rectangle((x, y, x + width, y + thickness), fill=GREEN, outline=DARK, width=3)
    if inner:
        draw.rectangle((x + 58, y, x + 132, y + thickness), fill="white", outline=DARK, width=2)
    draw.line((x - 14, y + thickness / 2, x + width + 14, y + thickness / 2), fill=MID, width=2)


TEXT = {
    "de": {
        "types": ("Zahnradtyp", "Außen / Innen / Kette"), "teeth": ("Zähnezahl", "z = Anzahl der Zähne"),
        "component": ("3D-Bauteil", "Profil + Extrusion"), "pressure": ("Eingriffswinkel", "α an der Zahnflanke"),
        "backlash": ("Flankenspiel", "j zwischen Zahnflanken"), "bore": ("Innenbohrung", "Nur Material innen entfernen"),
        "module": ("Modul", "m = d / z"), "pitch": ("Kreisteilung", "p = π · m auf Teilkreis"),
        "diameters": ("Bezugsdurchmesser", "da / d / df getrennt"), "thickness": ("Bauteildicke", "Axiale Extrusion b"),
        "internal": ("Ringwand", "s hinter dem Zahnfuß"), "tip-radius": ("Zahnspitzenradius", "ra: Mitte bis Zahnspitze"),
        "root-radius": ("Zahnfußradius", "rf: Mitte bis Zahngrund"), "chain-pitch": ("Kettenteilung", "p: Rollenmitte zu Rollenmitte"),
        "chain-width": ("Innere Kettenbreite", "bi zwischen Innenlaschen"), "roller": ("Rolle und Rollensitz", "R = dr / 2 + Spiel c"),
        "connector": ("Verbinderwand", "s beidseitig abziehen"),
    },
    "en": {
        "types": ("Gear type", "External / internal / chain"), "teeth": ("Tooth count", "z = number of teeth"),
        "component": ("3D component", "Profile + extrusion"), "pressure": ("Pressure angle", "α at the tooth flank"),
        "backlash": ("Backlash", "j between tooth flanks"), "bore": ("Centre bore", "Removes centre material only"),
        "module": ("Module", "m = d / z"), "pitch": ("Circular pitch", "p = π · m on pitch circle"),
        "diameters": ("Reference diameters", "da / d / df shown separately"), "thickness": ("Part thickness", "Axial extrusion b"),
        "internal": ("Ring wall", "s behind the tooth root"), "tip-radius": ("Tooth-tip radius", "ra: centre to tooth tip"),
        "root-radius": ("Tooth-root radius", "rf: centre to tooth root"), "chain-pitch": ("Chain pitch", "p: roller centre to centre"),
        "chain-width": ("Inside chain width", "bi between inner plates"), "roller": ("Roller and seat", "R = dr / 2 + clearance c"),
        "connector": ("Connector wall", "subtract s on both sides"),
    },
}


def render(key, locale):
    title, subtitle = TEXT[locale][key]
    image, draw = canvas(title, subtitle)
    if key == "types":
        for x, kind, label in ((65, "external", "A"), (190, "internal", "I"), (315, "sprocket", "K" if locale == "de" else "C")):
            old = gear_points(teeth=10, radius=52, cx=x, cy=245)
            if kind == "internal":
                draw.ellipse((x - 60, 185, x + 60, 305), fill=DARK)
                draw.polygon(old, fill="white")
            else:
                draw.polygon(old, fill=GREEN, outline=DARK)
                draw.ellipse((x - 16, 229, x + 16, 261), fill="white", outline=DARK, width=2)
            draw.text((x - 8, 330), label, fill=ORANGE, font=font(22, True))
    else:
        kind = "internal" if key == "internal" else "sprocket" if key in {"chain-pitch", "chain-width", "roller", "connector"} else "external"
        front_gear(draw, kind, bore=True, reference=key not in {"component", "thickness", "chain-width", "connector"})

    if key == "teeth":
        draw.arc((52, 62, 328, 338), 210, 320, fill=ORANGE, width=5)
        draw.text((92, 332), "z = 14", fill=ORANGE, font=font(24, True))
    elif key == "component":
        side_view(draw, 375, 225, 205, 55)
        draw.line((190, 330, 375, 280), fill=ORANGE, width=3)
        draw.text((392, 310), "3D", fill=ORANGE, font=font(26, True))
    elif key == "pressure":
        draw.line((190, 200, 305, 200), fill=BLUE, width=3)
        draw.line((190, 200, 288, 132), fill=ORANGE, width=4)
        draw.arc((155, 165, 245, 255), 315, 360, fill=ORANGE, width=4)
        draw.text((238, 170), "α", fill=ORANGE, font=font(28, True))
    elif key == "backlash":
        draw.rectangle((360, 170, 600, 300), fill="white", outline=MID, width=2)
        draw.polygon(((405, 285), (455, 195), (485, 285)), fill=GREEN, outline=DARK)
        draw.polygon(((495, 285), (525, 195), (575, 285)), fill=GREEN, outline=DARK)
        dimension(draw, (476, 225), (504, 225), "j")
    elif key == "bore":
        dimension(draw, (190, 200), (222, 200), "r")
        draw.text((360, 235), "OK - " + ("Zähne unverändert" if locale == "de" else "teeth unchanged"), fill=BLUE, font=font(18, True))
    elif key == "module":
        dimension(draw, (290, 200), (318, 200), "m")
        draw.text((380, 210), "m = d / z", fill=ORANGE, font=font(25, True))
    elif key == "pitch":
        a1, a2 = -0.28, 0.28
        p1 = (190 + 112 * math.cos(a1), 200 + 112 * math.sin(a1))
        p2 = (190 + 112 * math.cos(a2), 200 + 112 * math.sin(a2))
        dimension(draw, p1, p2, "p")
    elif key == "diameters":
        for radius, label, color, y in ((128, "da", ORANGE, 165), (112, "d", BLUE, 205), (101, "df", DARK, 245)):
            draw.line((190, 200, 190 + radius, 200), fill=color, width=3)
            draw.text((375, y), f"{label} = {2*radius/5:.1f} mm", fill=color, font=font(19, True))
    elif key == "thickness":
        side_view(draw, 375, 210, 205, 62)
        dimension(draw, (600, 210), (600, 272), "b", extensions=[((580, 210), (612, 210)), ((580, 272), (612, 272))])
    elif key == "internal":
        dimension(draw, (55, 200), (88, 200), "s")
        draw.text((365, 220), "s", fill=ORANGE, font=font(30, True))
    elif key == "tip-radius":
        dimension(draw, (190, 200), (304, 142), "ra")
    elif key == "root-radius":
        dimension(draw, (190, 200), (291, 200), "rf")
    elif key == "chain-pitch":
        a = math.pi / 6
        p1 = (190 + 99 * math.cos(-a), 200 + 99 * math.sin(-a))
        p2 = (190 + 99 * math.cos(a), 200 + 99 * math.sin(a))
        dimension(draw, p1, p2, "p")
        draw.ellipse((p1[0]-7, p1[1]-7, p1[0]+7, p1[1]+7), fill=ORANGE)
        draw.ellipse((p2[0]-7, p2[1]-7, p2[0]+7, p2[1]+7), fill=ORANGE)
    elif key in {"chain-width", "connector"}:
        draw.rectangle((365, 185, 405, 285), fill=DARK)
        draw.rectangle((555, 185, 595, 285), fill=DARK)
        draw.rectangle((405, 210, 555, 260), fill=GREEN, outline=DARK, width=2)
        if key == "chain-width":
            dimension(draw, (405, 315), (555, 315), "bi", extensions=[((405, 270), (405, 325)), ((555, 270), (555, 325))])
        else:
            dimension(draw, (405, 315), (435, 315), "s", extensions=[((405, 270), (405, 325)), ((435, 270), (435, 325))])
    elif key == "roller":
        draw.rectangle((365, 170, 600, 330), fill="white", outline=MID, width=2)
        draw.arc((405, 190, 545, 330), 180, 360, fill=DARK, width=8)
        draw.ellipse((438, 205, 512, 279), fill=GREY, outline=DARK, width=3)
        dimension(draw, (475, 242), (512, 242), "dr/2")
        dimension(draw, (512, 190), (520, 182), "c")

    out = ROOT / "resources" / "toolclips" / locale
    out.mkdir(parents=True, exist_ok=True)
    image.save(out / f"{key}.png", optimize=True)


def build():
    command = ROOT / "resources" / "command"
    command.mkdir(parents=True, exist_ok=True)
    for size in (16, 32, 64):
        image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        scale = size / 380
        pts = [(x * scale, y * scale) for x, y in gear_points(cx=190, cy=190, radius=170)]
        draw.polygon(pts, fill=GREEN, outline=DARK)
        draw.ellipse((size * .34, size * .34, size * .66, size * .66), fill="white", outline=DARK, width=max(1, size // 32))
        image.save(command / f"{size}x{size}.png")
    for locale in ("de", "en"):
        for key in TEXT[locale]:
            render(key, locale)


if __name__ == "__main__":
    build()
