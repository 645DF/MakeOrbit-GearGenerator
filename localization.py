"""German/English UI strings. German is used only for Fusion's German UI."""

DE = {
    "command": "MakeOrbit GearGenerator", "description": "Stirn-, Innen- und Kettenräder automatisch erzeugen",
    "basic": "Grunddaten", "dimensions": "Optionale Maße", "chain": "Kette", "export": "Export & MakeOrbit",
    "type": "Zahnradtyp", "external": "Außenverzahnung", "internal": "Innenverzahnung", "sprocket": "Kettenrad",
    "teeth": "Zähnezahl (Pflicht)", "pressure": "Eingriffswinkel", "backlash": "Flankenspiel",
    "thickness": "Bauteildicke", "bore": "Innenradius verwenden", "bore_radius": "Innenradius",
    "use": "Vorgeben", "module": "Modul", "circular_pitch": "Kreisteilung", "pitch_diameter": "Teilkreisdurchmesser",
    "outside_diameter": "Außendurchmesser", "root_diameter": "Fußkreisdurchmesser", "ring_wall": "Ringwandstärke",
    "tip_radius": "Zahnspitzen-Kreisradius", "root_radius": "Zahnfuß-Kreisradius", "link_length": "Kettengliedlänge / Teilung",
    "link_width": "Kettengliedbreite innen", "roller_diameter": "Kettenröllchen-Durchmesser",
    "roller_thickness": "Kettenröllchen-Dicke", "connector_wall": "Wandstärke der Rollenverbinder",
    "clearance": "Rollenspiel", "summary": "Berechnete Werte", "name": "Bauteilname",
    "value": "Wert", "preview": "Live-Vorschau anzeigen",
    "save_local": "Dateien lokal exportieren", "folder": "Exportordner", "makeorbit": "Direkt an MakeOrbit senden",
    "format_step": "STEP", "format_stl": "STL", "format_3mf": "3MF", "format_dxf": "DXF",
    "created": "Zahnrad wurde erzeugt", "error": "Zahnrad konnte nicht erzeugt werden",
    "makeorbit_note": "MakeOrbit verwendet eine authentifizierte, ausschließlich lokale Verbindung. Direkte DXF-Übergabe benötigt MakeOrbit 2.9.9 oder neuer.",
}

EN = {
    "command": "MakeOrbit GearGenerator", "description": "Automatically create external, internal and chain gears",
    "basic": "Basics", "dimensions": "Optional dimensions", "chain": "Chain", "export": "Export & MakeOrbit",
    "type": "Gear type", "external": "External gear", "internal": "Internal gear", "sprocket": "Chain sprocket",
    "teeth": "Tooth count (required)", "pressure": "Pressure angle", "backlash": "Backlash",
    "thickness": "Part thickness", "bore": "Use bore radius", "bore_radius": "Bore radius",
    "use": "Specify", "module": "Module", "circular_pitch": "Circular pitch", "pitch_diameter": "Pitch diameter",
    "outside_diameter": "Outside diameter", "root_diameter": "Root diameter", "ring_wall": "Ring wall thickness",
    "tip_radius": "Tooth-tip circle radius", "root_radius": "Tooth-root circle radius", "link_length": "Chain link length / pitch",
    "link_width": "Inside chain link width", "roller_diameter": "Chain roller diameter",
    "roller_thickness": "Chain roller thickness", "connector_wall": "Roller connector wall thickness",
    "clearance": "Roller clearance", "summary": "Calculated values", "name": "Component name",
    "value": "Value", "preview": "Show live preview",
    "save_local": "Export files locally", "folder": "Export folder", "makeorbit": "Send directly to MakeOrbit",
    "format_step": "STEP", "format_stl": "STL", "format_3mf": "3MF", "format_dxf": "DXF",
    "created": "Gear was created", "error": "Gear could not be created",
    "makeorbit_note": "MakeOrbit uses an authenticated local-only connection. Direct DXF transfer requires MakeOrbit 2.9.9 or newer.",
}


def language_from_fusion(app):
    try:
        value = app.preferences.generalPreferences.userLanguage
        german = getattr(__import__("adsk.core", fromlist=["UserLanguages"]), "UserLanguages").GermanLanguage
        return "de" if value == german else "en"
    except Exception:
        return "en"


def translator(language):
    table = DE if language == "de" else EN
    return lambda key: table.get(key, key)
