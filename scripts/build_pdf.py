#!/usr/bin/env python3
"""Create the bilingual MakeOrbit GearGenerator user guide PDF."""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Frame, Image, KeepTogether, PageBreak, PageTemplate,
    Paragraph, Spacer, Table, TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "MakeOrbit_GearGenerator_Anleitung_DE_EN.pdf"
GREEN = colors.HexColor("#5f8172")
DARK = colors.HexColor("#17312a")
PALE = colors.HexColor("#eef3f0")
ORANGE = colors.HexColor("#e68032")
GREY = colors.HexColor("#52645d")


def register_fonts():
    regular = Path("/System/Library/Fonts/Supplemental/Arial.ttf")
    bold = Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf")
    if not regular.exists():
        regular = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
        bold = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
    pdfmetrics.registerFont(TTFont("Guide", str(regular)))
    pdfmetrics.registerFont(TTFont("Guide-Bold", str(bold)))


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(GREEN); canvas.setLineWidth(0.6)
    canvas.line(18 * mm, 14 * mm, 192 * mm, 14 * mm)
    canvas.setFont("Guide", 8); canvas.setFillColor(GREY)
    canvas.drawString(18 * mm, 9 * mm, "MakeOrbit GearGenerator 1.0.0")
    canvas.drawRightString(192 * mm, 9 * mm, "645DF | %d" % doc.page)
    canvas.restoreState()


def styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("title", parent=base["Title"], fontName="Guide-Bold", fontSize=28,
                                leading=33, textColor=DARK, alignment=TA_CENTER, spaceAfter=10 * mm),
        "subtitle": ParagraphStyle("subtitle", parent=base["Normal"], fontName="Guide", fontSize=13,
                                   leading=18, textColor=GREY, alignment=TA_CENTER, spaceAfter=6 * mm),
        "h1": ParagraphStyle("h1", parent=base["Heading1"], fontName="Guide-Bold", fontSize=20,
                             leading=24, textColor=DARK, spaceBefore=4 * mm, spaceAfter=4 * mm),
        "h2": ParagraphStyle("h2", parent=base["Heading2"], fontName="Guide-Bold", fontSize=13,
                             leading=16, textColor=GREEN, spaceBefore=3 * mm, spaceAfter=2 * mm),
        "body": ParagraphStyle("body", parent=base["BodyText"], fontName="Guide", fontSize=9.7,
                               leading=14, textColor=DARK, spaceAfter=2.5 * mm),
        "bullet": ParagraphStyle("bullet", parent=base["BodyText"], fontName="Guide", fontSize=9.4,
                                 leading=13, leftIndent=5 * mm, firstLineIndent=-3 * mm, textColor=DARK, spaceAfter=1.7 * mm),
        "note": ParagraphStyle("note", parent=base["BodyText"], fontName="Guide", fontSize=9.2,
                               leading=13, textColor=DARK, backColor=PALE, borderColor=GREEN,
                               borderWidth=0.8, borderPadding=8, spaceBefore=2 * mm, spaceAfter=4 * mm),
        "small": ParagraphStyle("small", parent=base["BodyText"], fontName="Guide", fontSize=8,
                                leading=11, textColor=GREY),
    }


def p(text, style):
    return Paragraph(text, style)


def bullets(items, st):
    return [p("• " + item, st["bullet"]) for item in items]


def clip(name, width=76 * mm):
    path = ROOT / "resources" / "toolclips" / name
    return Image(str(path), width=width, height=width * 300 / 480)


def parameter_table(st, german=True):
    if german:
        rows = [
            ("Zähnezahl", "Pflichtangabe; bestimmt Teilungswinkel und Wiederholung."),
            ("Modul / Kreisteilung", "Optionale Leitgröße für die physische Zahnradgröße."),
            ("Teilkreis", "Theoretischer Abrollkreis zweier Zahnräder."),
            ("Außen- / Fußkreis", "Radien an Zahnspitze und Zahnfuß; Vorgaben werden exakt berücksichtigt."),
            ("Innenradius", "Optional. Deaktiviert bedeutet ein geschlossenes Bauteil."),
            ("Bauteildicke", "Axiale Extrusion des fertigen Konstruktionsteils."),
        ]
        head = ("Parameter", "Bedeutung")
    else:
        rows = [
            ("Tooth count", "Required; controls pitch angle and repetition."),
            ("Module / circular pitch", "Optional leading dimension for physical gear size."),
            ("Pitch circle", "Theoretical rolling circle of two mating gears."),
            ("Outside / root circle", "Tooth-tip and tooth-root radii; explicit values are honoured."),
            ("Bore radius", "Optional. Disabled creates a closed part."),
            ("Part thickness", "Axial extrusion of the finished component."),
        ]
        head = ("Parameter", "Meaning")
    data = [[p("<b>%s</b>" % head[0], st["body"]), p("<b>%s</b>" % head[1], st["body"])]]
    data += [[p(a, st["body"]), p(b, st["body"])] for a, b in rows]
    table = Table(data, colWidths=[50 * mm, 119 * mm], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), GREEN), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("VALIGN", (0, 0), (-1, -1), "TOP"), ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#b8c8c1")),
        ("BACKGROUND", (0, 1), (-1, -1), colors.white), ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6), ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return table


def source_table(st):
    rows = [
        ("Autodesk Fusion API - Creating a Script or Add-In", "Manifest, macOS/Windows add-in locations, supportedOS and startup behavior."),
        ("Autodesk Fusion API - Design.exportManager", "Supported programmatic STEP, STL and 3MF export workflow."),
        ("Autodesk Fusion API - CommandInput.toolClipFilename", "Progressive tooltip image support used for parameter graphics."),
        ("Autodesk Fusion API - GeneralPreferences.userLanguage", "Fusion language detection for German/English selection."),
    ]
    data = [[p("<b>Official source</b>", st["body"]), p("<b>Use in this add-in</b>", st["body"])]]
    data += [[p(a, st["small"]), p(b, st["small"])] for a, b in rows]
    table = Table(data, colWidths=[72 * mm, 97 * mm], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), DARK), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("VALIGN", (0, 0), (-1, -1), "TOP"), ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#b8c8c1")),
        ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return table


def build_story(st):
    story = [Spacer(1, 20 * mm), clip("types.png", 120 * mm), Spacer(1, 12 * mm),
             p("MakeOrbit GearGenerator", st["title"]),
             p("Ausführliche Anleitung für Autodesk Fusion<br/>Comprehensive guide for Autodesk Fusion", st["subtitle"]),
             p("Version 1.0.0 | Deutsch + English | macOS + Windows", st["note"]), PageBreak()]

    story += [p("Deutsch", st["h1"]), p("1. Überblick", st["h2"]),
              p("MakeOrbit GearGenerator erzeugt Außenverzahnungen, Innenverzahnungen und Kettenräder als neue, extrudierte Fusion-Bauteile. Die Zähnezahl ist die einzige Pflichtangabe. Alle übrigen Größen können einzeln aktiviert werden; nicht angegebene Maße werden berechnet.", st["body"])]
    story += bullets([
        "Außenverzahnung mit Evolventenflanken, Eingriffswinkel und Flankenspiel.",
        "Innenverzahnung mit berechneter oder vorgegebener Ringwand.",
        "Kettenrad aus Teilung, Innenbreite, Röllchendurchmesser, Röllchendicke und optionaler Verbinderwand.",
        "Geschlossene Standardausführung; eine Mittelöffnung entsteht nur bei aktiviertem Innenradius.",
        "STEP, STL, 3MF und DXF lokal; alle vier Formate direkt an MakeOrbit 2.9.9.",
        "Deutsche Oberfläche nur bei deutscher Fusion-Systemsprache, sonst Englisch.",
    ], st)
    story += [p("Wichtige Größen", st["h2"]), parameter_table(st, True), PageBreak()]

    story += [p("2. Installation", st["h1"]), p("macOS", st["h2"])]
    story += bullets([
        "GitHub-Release laden und vollständig entpacken.",
        "Im Ordner <b>installers</b> die Datei <b>Install MakeOrbit GearGenerator.command</b> doppelklicken.",
        "Fusion neu starten oder unter Dienstprogramme > Zusatzmodule > Skripte und Zusatzmodule starten.",
        "Der Befehl erscheint unter Volumenkörper > Erstellen.",
    ], st)
    story += [p("Manueller Zielordner:<br/><font name='Guide-Bold'>~/Library/Application Support/Autodesk/Autodesk Fusion 360/API/AddIns/MakeOrbitGearGenerator</font>", st["note"]),
              p("Windows", st["h2"])]
    story += bullets([
        "GitHub-Release laden und vollständig entpacken.",
        "Install-MakeOrbitGearGenerator.ps1 mit PowerShell ausführen.",
        "Fusion neu starten oder das Zusatzmodul manuell starten.",
    ], st)
    story += [p("Manueller Zielordner:<br/><font name='Guide-Bold'>%APPDATA%\\Autodesk\\Autodesk Fusion 360\\API\\AddIns\\MakeOrbitGearGenerator</font>", st["note"]),
              p("Die Installer benötigen keine Administratorrechte. Beim Aktualisieren bleibt eine unmittelbar vorherige Kopie als <b>MakeOrbitGearGenerator.previous</b> erhalten.", st["body"]), PageBreak()]

    story += [p("3. Zahnrad erzeugen", st["h1"]),
              Table([[clip("teeth.png", 78 * mm), clip("diameters.png", 78 * mm)]], colWidths=[84 * mm, 84 * mm]),
              Spacer(1, 4 * mm)]
    story += bullets([
        "Zahnradtyp und Bauteilnamen wählen.",
        "Zähnezahl eingeben: mindestens 8, bei Kettenrädern mindestens 6.",
        "Optional Innenradius aktivieren. Ohne Aktivierung bleibt das Bauteil geschlossen.",
        "Unter Optionale Maße nur feste Werte aktivieren. Mehrere Angaben dürfen höchstens 2 Prozent voneinander abweichen.",
        "Berechnete Werte kontrollieren und mit OK erzeugen.",
    ], st)
    story += [p("Ohne physische Leitgröße gilt Modul 2 mm. Die Zähnezahl allein kann die physische Größe mathematisch nicht eindeutig bestimmen; deshalb verwendet das Plug-in diesen dokumentierten Standardwert.", st["note"]),
              p("Formeln", st["h2"]),
              p("Modul: <b>m = d / z</b><br/>Kreisteilung: <b>p = πm</b><br/>Außenrad: <b>r<sub>a</sub> = r<sub>p</sub> + m</b>, <b>r<sub>f</sub> = r<sub>p</sub> - 1,25m</b>", st["body"]), PageBreak()]

    story += [p("4. Kettenrad", st["h1"]),
              Table([[clip("chain-pitch.png", 78 * mm), clip("roller.png", 78 * mm)]], colWidths=[84 * mm, 84 * mm]),
              Spacer(1, 4 * mm),
              p("Die Kettengliedlänge wird als Teilung verwendet. Der Teilkreisradius lautet <b>r<sub>p</sub> = p / (2 sin(π/z))</b>. Für jedes Röllchen wird eine echte Kreisbogentasche mit <b>R = d<sub>Rolle</sub>/2 + Spiel</b> erzeugt.", st["body"])]
    story += bullets([
        "Kettengliedbreite und Röllchendicke bestimmen die maximal nutzbare Bauteildicke.",
        "Eine optionale Verbinderwand wird auf beiden Seiten abgezogen.",
        "Ein explizit vorgegebener Außendurchmesser überschreibt die berechnete Zahnspitzenhöhe.",
        "Zu große Rollen für eine kleine Zähnezahl werden mit einer verständlichen Fehlermeldung abgelehnt.",
    ], st)
    story += [p("5. Export und MakeOrbit", st["h1"]),
              p("Der Generator kann STEP, STL, 3MF und DXF in den gewählten Ordner schreiben. MakeOrbit verwendet eine authentifizierte lokale Verbindung auf 127.0.0.1; CAD-Dateien werden dabei nicht in eine Cloud geladen.", st["body"]),
              p("MakeOrbit 2.9.8 akzeptiert STEP, STL und 3MF. MakeOrbit 2.9.9 oder neuer speichert auch DXF direkt.", st["note"]),
              p("Ist MakeOrbit nicht installiert oder nicht erreichbar, erscheint pro Importversuch ein dezenter Hinweis. Unter macOS kann auf Wunsch <b>https://645df.de/makeorbit-beta</b> mit Informationen zum aktuellen Betatest geöffnet werden. Unter Windows wird auf die geplante Windows-Version hingewiesen. Lokale Exportdateien bleiben erhalten.", st["body"]), PageBreak()]

    story += [p("English", st["h1"]), p("1. Overview", st["h2"]),
              p("MakeOrbit GearGenerator creates external involute gears, internal ring gears, and chain sprockets as new extruded Fusion components. Tooth count is the only required input. Every other size can be enabled individually, and missing dimensions are calculated.", st["body"])]
    story += bullets([
        "External involute teeth with pressure angle and backlash.",
        "Internal teeth with calculated or explicit ring wall.",
        "Sprockets from pitch, inside width, roller diameter, roller thickness, and optional connector wall.",
        "Closed by default; a centre opening is created only when bore radius is enabled.",
        "Local STEP, STL, 3MF, and DXF; direct transfer of all four formats to MakeOrbit 2.9.9.",
        "German UI only when Fusion is set to German; English for all other languages.",
    ], st)
    story += [p("Key dimensions", st["h2"]), parameter_table(st, False), PageBreak()]

    story += [p("2. Installation", st["h1"]), p("macOS", st["h2"])]
    story += bullets([
        "Download and fully extract the GitHub release.",
        "Double-click <b>Install MakeOrbit GearGenerator.command</b> in <b>installers</b>.",
        "Restart Fusion or start the add-in under Utilities > Add-ins > Scripts and Add-ins.",
        "The command appears under Solid > Create.",
    ], st)
    story += [p("Manual destination:<br/><font name='Guide-Bold'>~/Library/Application Support/Autodesk/Autodesk Fusion 360/API/AddIns/MakeOrbitGearGenerator</font>", st["note"]),
              p("Windows", st["h2"])]
    story += bullets([
        "Download and fully extract the GitHub release.",
        "Run Install-MakeOrbitGearGenerator.ps1 with PowerShell.",
        "Restart Fusion or start the add-in manually.",
    ], st)
    story += [p("Manual destination:<br/><font name='Guide-Bold'>%APPDATA%\\Autodesk\\Autodesk Fusion 360\\API\\AddIns\\MakeOrbitGearGenerator</font>", st["note"]),
              p("The installers need no administrator rights. During an update, one immediately previous copy is retained as <b>MakeOrbitGearGenerator.previous</b>.", st["body"]), PageBreak()]

    story += [p("3. Create a gear", st["h1"]),
              Table([[clip("pressure.png", 78 * mm), clip("internal.png", 78 * mm)]], colWidths=[84 * mm, 84 * mm]),
              Spacer(1, 4 * mm)]
    story += bullets([
        "Choose the gear type and component name.",
        "Enter tooth count: at least 8, or 6 for a sprocket.",
        "Optionally enable bore radius. Disabled produces a closed part.",
        "Enable only fixed values under Optional dimensions. Multiple inputs must agree within 2 percent.",
        "Review Calculated values and press OK.",
    ], st)
    story += [p("Without a physical leading dimension, module defaults to 2 mm. Tooth count alone cannot mathematically determine physical size, so the add-in uses this documented standard.", st["note"]),
              p("Formulas", st["h2"]),
              p("Module: <b>m = d / z</b><br/>Circular pitch: <b>p = πm</b><br/>External gear: <b>r<sub>a</sub> = r<sub>p</sub> + m</b>, <b>r<sub>f</sub> = r<sub>p</sub> - 1.25m</b>", st["body"]), PageBreak()]

    story += [p("4. Chain sprocket", st["h1"]),
              Table([[clip("chain-width.png", 78 * mm), clip("connector.png", 78 * mm)]], colWidths=[84 * mm, 84 * mm]),
              Spacer(1, 4 * mm),
              p("Chain link length is used as pitch. Pitch radius is <b>r<sub>p</sub> = p / (2 sin(π/z))</b>. Every roller receives a true circular seating pocket with <b>R = d<sub>roller</sub>/2 + clearance</b>.", st["body"])]
    story += bullets([
        "Inside link width and roller thickness limit usable part thickness.",
        "Optional connector wall is subtracted on both sides.",
        "An explicit outside diameter overrides the calculated tooth-tip height.",
        "Rollers that are too large for a small tooth count are rejected with a clear error.",
    ], st)
    story += [p("5. Export and MakeOrbit", st["h1"]),
              p("The generator can write STEP, STL, 3MF, and DXF into the selected folder. MakeOrbit uses an authenticated local connection on 127.0.0.1; CAD files are not uploaded to a cloud service.", st["body"]),
              p("MakeOrbit 2.9.8 accepts STEP, STL, and 3MF. MakeOrbit 2.9.9 or newer also stores DXF directly.", st["note"]),
              p("If MakeOrbit is not installed or cannot be reached, one unobtrusive notice appears per import attempt. On macOS, the user may open <b>https://645df.de/makeorbit-beta</b> for information about the current beta test. On Windows, the dialog explains that a Windows version is planned. Local export files are retained.", st["body"]), PageBreak()]

    story += [p("Troubleshooting / Fehlerbehebung", st["h1"]),
              p("<b>Command missing / Befehl fehlt</b><br/>Restart Fusion and confirm that MakeOrbitGearGenerator is running in Scripts and Add-ins.", st["body"]),
              p("<b>Conflicting dimensions / Widersprüchliche Maße</b><br/>Use one leading size or ensure all enabled values imply the same module within 2 percent.", st["body"]),
              p("<b>MakeOrbit unreachable / nicht erreichbar</b><br/>Open MakeOrbit and reinstall its Fusion integration once so the local token file is available.", st["body"]),
              p("<b>Profile not closed / Profil nicht geschlossen</b><br/>Increase tooth count or avoid extreme combinations of backlash, module, and diameters.", st["body"]),
              p("Official technical references", st["h2"]), source_table(st), Spacer(1, 4 * mm),
              p("Source URLs: help.autodesk.com/cloudhelp/ENU/Fusion-360-API/", st["small"]),
              p("License / Lizenz", st["h2"]),
              p("The public source is <b>not open source</b>. An unmodified official release may be used privately and non-commercially. Copying, modifying, redistributing, embedding, reusing in another function or app, and commercial use are prohibited without prior written permission from Michael Jäger / 645DF. Paid special-purpose or commercial rights may be negotiated separately. The repository's LICENSE file contains the binding terms.", st["body"]),
              p("Der öffentliche Quellcode ist <b>nicht Open Source</b>. Eine unveränderte offizielle Version darf privat und nichtkommerziell verwendet werden. Kopieren, Verändern, Weitergeben, Einbauen, Wiederverwenden und kommerzielle Nutzung sind ohne vorherige schriftliche Erlaubnis untersagt. Maßgeblich ist die Datei LICENSE.", st["body"]),
              p("Autodesk Fusion und MakeOrbit bleiben eigenständige Produkte; dieses Zusatzmodul enthält keine Autodesk-Binärdateien oder Zugangsdaten.", st["note"])]
    return story


def main():
    register_fonts(); st = styles(); OUT.parent.mkdir(parents=True, exist_ok=True)
    doc = BaseDocTemplate(str(OUT), pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm,
                          topMargin=18 * mm, bottomMargin=18 * mm,
                          title="MakeOrbit GearGenerator - Anleitung / User Guide",
                          author="645DF")
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="main")
    doc.addPageTemplates([PageTemplate(id="guide", frames=[frame], onPage=footer)])
    doc.build(build_story(st))
    print(OUT)


if __name__ == "__main__":
    main()
