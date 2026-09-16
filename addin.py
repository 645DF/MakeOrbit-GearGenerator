"""Fusion UI and solid creation for MakeOrbit GearGenerator."""

import json
import os
import pathlib
import platform
import tempfile
import traceback
import webbrowser

import adsk.core
import adsk.fusion

try:
    from .gear_core import GearRequest, GearError, calculate, outline
    from .localization import language_from_fusion, translator
    from .makeorbit_bridge import send_file, MakeOrbitError, unavailable_guidance
except ImportError:
    from gear_core import GearRequest, GearError, calculate, outline
    from localization import language_from_fusion, translator
    from makeorbit_bridge import send_file, MakeOrbitError, unavailable_guidance


COMMAND_ID = "de_645df_fusion_gear_generator"
WORKSPACE_ID = "FusionSolidEnvironment"
PANEL_ID = "SolidCreatePanel"
ADDIN_DIR = os.path.dirname(os.path.abspath(__file__))
RESOURCE_DIR = os.path.join(ADDIN_DIR, "resources", "command")
TOOLCLIP_DIR = os.path.join(ADDIN_DIR, "resources", "toolclips")
_handlers = []
_control = None
_definition = None


def _localized(german, german_text, english_text):
    return german_text if german else english_text


def _toolclip(input_obj, filename, short, long_text, german=False):
    input_obj.tooltip = short
    input_obj.tooltipDescription = long_text
    path = os.path.join(TOOLCLIP_DIR, "de" if german else "en", filename)
    if not os.path.isfile(path):
        path = os.path.join(TOOLCLIP_DIR, filename)
    if os.path.isfile(path):
        input_obj.toolClipFilename = path
    return input_obj


def _length(inputs, input_id, label, expression, clip="diameters.png", tip="", german=False):
    value = inputs.addValueInput(input_id, label, "mm", adsk.core.ValueInput.createByString(expression))
    return _toolclip(value, clip, label, tip or label, german)


def _optional(group, key, label, value_label, expression, clip, tip, german=False, enabled=False):
    toggle = group.addBoolValueInput("use_" + key, label, True, "", enabled)
    _toolclip(toggle, clip, label, tip, german)
    value = _length(group, key, value_label, expression, clip, tip, german)
    value.isVisible = True
    value.isEnabled = enabled
    return toggle, value


def _selected_kind(inputs):
    item = inputs.itemById("gear_type").selectedItem
    if not item:
        return "external"
    return {0: "external", 1: "internal", 2: "sprocket"}.get(item.index, "external")


def _mm(inputs, input_id):
    item = inputs.itemById(input_id)
    return float(item.value) * 10.0


def _optional_mm(inputs, input_id):
    toggle = inputs.itemById("use_" + input_id)
    return _mm(inputs, input_id) if toggle and toggle.value else None


def _request(inputs):
    kind = _selected_kind(inputs)
    bore = _mm(inputs, "bore_radius") if inputs.itemById("use_bore").value and kind != "internal" else None
    return GearRequest(
        kind=kind, teeth=int(inputs.itemById("teeth").value),
        module=_optional_mm(inputs, "module"),
        circular_pitch=_optional_mm(inputs, "circular_pitch"),
        pitch_diameter=_optional_mm(inputs, "pitch_diameter"),
        outside_diameter=_optional_mm(inputs, "outside_diameter"),
        root_diameter=_optional_mm(inputs, "root_diameter"),
        pressure_angle_deg=float(inputs.itemById("pressure_angle").value) * 180.0 / 3.141592653589793,
        backlash=_mm(inputs, "backlash"), thickness=_optional_mm(inputs, "thickness"),
        bore_radius=bore, ring_wall=_optional_mm(inputs, "ring_wall"),
        tip_radius=_optional_mm(inputs, "tip_radius"), root_radius=_optional_mm(inputs, "root_radius"),
        chain_link_length=_mm(inputs, "chain_link_length"),
        chain_link_width=_mm(inputs, "chain_link_width"),
        roller_diameter=_mm(inputs, "roller_diameter"),
        roller_thickness=_mm(inputs, "roller_thickness"),
        connector_wall=_optional_mm(inputs, "connector_wall"),
        roller_clearance=_mm(inputs, "roller_clearance"),
    )


def _summary(result, german):
    labels = (("Teilkreis", "Pitch circle"), ("Außenkreis", "Outside circle"),
              ("Fußkreis", "Root circle"), ("Dicke", "Thickness"))
    values = (result.pitch_diameter, result.outside_diameter, result.root_diameter, result.thickness)
    lines = ["%s: %.3f mm" % (label[0 if german else 1], value) for label, value in zip(labels, values)]
    lines.insert(0, ("Modul" if german else "Module") + ": %.4g mm" % result.module)
    if result.roller_seat_radius is not None:
        lines.append(("Rollensitzradius" if german else "Roller seat radius") + ": %.3f mm" % result.roller_seat_radius)
    return "<br>".join(lines)


def _error_text(error, german):
    text = str(error)
    if not german:
        return text
    translations = (
        ("Conflicting size inputs", "Widersprüchliche Maßvorgaben"),
        ("Tooth count is required", "Die Zähnezahl ist erforderlich"),
        ("Pressure angle must be between 5 and 35 degrees", "Der Eingriffswinkel muss zwischen 5 und 35 Grad liegen"),
        ("Bore radius must be smaller", "Der Innenradius muss kleiner als der Zahnfuß- beziehungsweise Kettenradgrundradius sein"),
        ("Connector wall thickness leaves no room", "Die Verbinderwand lässt keine nutzbare Kettenradbreite übrig"),
        ("Outside radius must be larger", "Der Außenradius muss größer als der Zahnfußradius sein"),
        ("Internal gear outside radius", "Der Außenradius der Innenverzahnung muss Zahnfuß und Ringwand einschließen"),
        ("Roller seat is too large", "Der Rollensitz ist für die gewählte Zähnezahl zu groß"),
        ("Tooth geometry is not feasible", "Die Zahngeometrie ist mit diesen Werten nicht möglich"),
        ("Invalid external radii", "Ungültige Radien der Außenverzahnung"),
        ("must be positive", "muss größer als null sein"),
        ("Fusion could not resolve a closed profile", "Fusion konnte kein geschlossenes Profil erkennen"),
    )
    for english, german_text in translations:
        if english in text:
            if english == "must be positive":
                return "Der eingegebene Wert " + german_text
            return german_text
    return "Bitte Eingaben und Maße prüfen."


def _show_makeorbit_unavailable(ui, german):
    message, url = unavailable_guidance(platform.system(), german)
    if url:
        answer = ui.messageBox(
            message, "MakeOrbit",
            adsk.core.MessageBoxButtonTypes.YesNoButtonType,
            adsk.core.MessageBoxIconTypes.InformationIconType,
        )
        if answer == adsk.core.DialogResults.DialogYes:
            webbrowser.open(url)
    else:
        ui.messageBox(
            message, "MakeOrbit",
            adsk.core.MessageBoxButtonTypes.OKButtonType,
            adsk.core.MessageBoxIconTypes.InformationIconType,
        )


def _set_visibility(inputs):
    kind = _selected_kind(inputs)
    for key in ("chain_link_length", "chain_link_width", "roller_diameter", "roller_thickness", "roller_clearance"):
        inputs.itemById(key).isVisible = kind == "sprocket"
    inputs.itemById("use_connector_wall").isVisible = kind == "sprocket"
    inputs.itemById("connector_wall").isVisible = kind == "sprocket"
    inputs.itemById("connector_wall").isEnabled = inputs.itemById("use_connector_wall").value
    for key in ("pressure_angle", "backlash"):
        inputs.itemById(key).isVisible = kind != "sprocket"
    inputs.itemById("use_bore").isVisible = kind != "internal"
    inputs.itemById("bore_radius").isVisible = kind != "internal"
    inputs.itemById("bore_radius").isEnabled = inputs.itemById("use_bore").value
    inputs.itemById("use_ring_wall").isVisible = kind == "internal"
    inputs.itemById("ring_wall").isVisible = kind == "internal"
    inputs.itemById("ring_wall").isEnabled = inputs.itemById("use_ring_wall").value
    for key in ("module", "circular_pitch", "pitch_diameter", "root_diameter"):
        inputs.itemById("use_" + key).isVisible = kind != "sprocket"
        inputs.itemById(key).isVisible = kind != "sprocket"
        inputs.itemById(key).isEnabled = inputs.itemById("use_" + key).value
    for key in ("outside_diameter", "thickness", "tip_radius", "root_radius"):
        inputs.itemById(key).isVisible = True
        inputs.itemById(key).isEnabled = inputs.itemById("use_" + key).value


def _update_summary(inputs, german):
    box = inputs.itemById("calculated_summary")
    try:
        box.formattedText = _summary(calculate(_request(inputs)), german)
    except Exception as error:
        box.formattedText = "<font color='red'>%s</font>" % _error_text(error, german)


class CommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self, german):
        super().__init__()
        self.german = german

    def notify(self, args):
        command = args.command
        command.isExecutedWhenPreEmpted = False
        t = translator("de" if self.german else "en")
        inputs = command.commandInputs

        basic = inputs.addTabCommandInput("basic_tab", t("basic")).children
        kind = basic.addDropDownCommandInput("gear_type", t("type"), adsk.core.DropDownStyles.TextListDropDownStyle)
        kind.listItems.add(t("external"), True); kind.listItems.add(t("internal"), False); kind.listItems.add(t("sprocket"), False)
        _toolclip(kind, "types.png", t("type"), _localized(self.german,
                  "Wähle Außenverzahnung, Innenverzahnung oder Kettenrad. Die Geometrie und die verfügbaren Maße passen sich automatisch an.",
                  "Choose an external gear, internal ring gear, or chain sprocket. Geometry and available dimensions adapt automatically."), self.german)
        teeth = basic.addIntegerSpinnerCommandInput("teeth", t("teeth"), 6, 400, 1, 20)
        _toolclip(teeth, "teeth.png", t("teeth"), _localized(self.german,
                  "Pflichtangabe. Sie bestimmt die Anzahl der gleichmäßig verteilten Zähne; fehlende Maße werden aus den aktivierten Vorgaben berechnet.",
                  "Required. Sets the number of equally spaced teeth; missing dimensions are calculated from the enabled inputs."), self.german)
        name = basic.addStringValueInput("component_name", t("name"), "MakeOrbit-Gear")
        _toolclip(name, "component.png", t("name"), _localized(self.german,
                  "Name des neuen Fusion-Bauteils, des Volumenkörpers und der Profilskizze.",
                  "Name of the new Fusion component, solid body, and profile sketch."), self.german)
        pressure = basic.addValueInput("pressure_angle", t("pressure"), "deg", adsk.core.ValueInput.createByString("20 deg"))
        _toolclip(pressure, "pressure.png", t("pressure"), _localized(self.german,
                  "Winkel zwischen der Eingriffslinie und der Tangente am Teilkreis. 20 Grad ist der übliche Standardwert.",
                  "Angle between the line of action and the pitch-circle tangent. 20 degrees is the common standard."), self.german)
        backlash = _length(basic, "backlash", t("backlash"), "0.05 mm", "backlash.png", _localized(self.german,
                            "Tangentiales Spiel zwischen zwei eingreifenden Zahnflanken.",
                            "Tangential clearance between two meshing tooth flanks."), self.german)
        bore_toggle = basic.addBoolValueInput("use_bore", t("bore"), True, "", False)
        bore_tip = _localized(self.german,
                             "Erzeugt ausschließlich eine zentrische Bohrung. Die Zahnkontur und ihre Lage bleiben unverändert. Deaktiviert bleibt das Zahnrad geschlossen.",
                             "Creates only a concentric bore. Tooth geometry and position remain unchanged. Disabled creates a closed gear.")
        _toolclip(bore_toggle, "bore.png", t("bore"), bore_tip, self.german)
        bore = _length(basic, "bore_radius", t("bore_radius"), "5 mm", "bore.png", bore_tip, self.german)
        bore.isEnabled = False
        preview = basic.addBoolValueInput("preview_enabled", t("preview"), True, "", True)
        _toolclip(preview, "component.png", t("preview"), _localized(self.german,
                  "Zeigt nach jeder gültigen Eingabe eine temporäre 3D-Vorschau. Beim Abbrechen entfernt Fusion die Vorschaugeometrie.",
                  "Shows a temporary 3D preview after every valid input change. Fusion removes preview geometry when cancelled."), self.german)

        dims = inputs.addTabCommandInput("dimensions_tab", t("dimensions")).children
        optional_specs = (
            ("module", "2 mm", "module.png", "Teilkreisdurchmesser geteilt durch Zähnezahl: m = d / z.", "Pitch diameter divided by tooth count: m = d / z."),
            ("circular_pitch", "6.283185 mm", "pitch.png", "Bogenabstand zweier benachbarter Zähne auf dem Teilkreis: p = πm.", "Arc distance between adjacent teeth on the pitch circle: p = πm."),
            ("pitch_diameter", "40 mm", "diameters.png", "Bezugsdurchmesser, auf dem zwei Zahnräder theoretisch schlupffrei abrollen.", "Reference diameter where two mating gears theoretically roll without slip."),
            ("outside_diameter", "44 mm", "diameters.png", "Gesamtdurchmesser über die Zahnspitzen; eine aktivierte Vorgabe wird exakt verwendet.", "Overall diameter across tooth tips; an enabled value is used exactly."),
            ("root_diameter", "35 mm", "diameters.png", "Durchmesser des Kreises durch die tiefsten Punkte zwischen den Zähnen.", "Diameter of the circle through the deepest points between teeth."),
            ("thickness", "5 mm", "thickness.png", "Axiale Extrusionsdicke des erzeugten Volumenkörpers.", "Axial extrusion thickness of the generated solid body."),
            ("ring_wall", "4 mm", "internal.png", "Materialstärke außerhalb der Zahnfüße einer Innenverzahnung.", "Material thickness outside the roots of an internal ring gear."),
            ("tip_radius", "22 mm", "tip-radius.png", "Radius von der Zahnradmitte bis zu den Zahnspitzen.", "Radius from the gear centre to the tooth tips."),
            ("root_radius", "17.5 mm", "root-radius.png", "Radius von der Zahnradmitte bis zum Zahnfuß.", "Radius from the gear centre to the tooth root."),
        )
        for key, expression, clip, de_tip, en_tip in optional_specs:
            _optional(dims, key, t(key), t("value"), expression, clip,
                      _localized(self.german, de_tip, en_tip), self.german)

        chain = inputs.addTabCommandInput("chain_tab", t("chain")).children
        _length(chain, "chain_link_length", t("link_length"), "12.7 mm", "chain-pitch.png", _localized(self.german,
                "Abstand von Rollenmitte zu Rollenmitte; dieser Wert wird zur Kettenradteilung.",
                "Distance from roller centre to roller centre; this becomes the sprocket pitch."), self.german)
        _length(chain, "chain_link_width", t("link_width"), "3.55 mm", "chain-width.png", _localized(self.german,
                "Freie Breite zwischen den inneren Kettenlaschen.", "Free width between the inner chain plates."), self.german)
        _length(chain, "roller_diameter", t("roller_diameter"), "7.75 mm", "roller.png", _localized(self.german,
                "Außendurchmesser der Kettenrolle; daraus wird die kreisförmige Rollentasche berechnet.",
                "Outside diameter of the chain roller; used to calculate the circular seating pocket."), self.german)
        _length(chain, "roller_thickness", t("roller_thickness"), "3.30 mm", "chain-width.png", _localized(self.german,
                "Axiale Breite der Kettenrolle; begrenzt die sichere Zahnbreite.",
                "Axial roller width; limits the safe tooth width."), self.german)
        _optional(chain, "connector_wall", t("connector_wall"), t("value"), "0.25 mm", "connector.png", _localized(self.german,
                  "Optionale seitliche Sicherheitszugabe; sie wird auf beiden Seiten von der nutzbaren Breite abgezogen.",
                  "Optional side allowance; subtracted from the usable width on both sides."), self.german)
        _length(chain, "roller_clearance", t("clearance"), "0.15 mm", "roller.png", _localized(self.german,
                "Radiales Zusatzspiel zum Rollenradius, damit die Rolle frei in der Tasche sitzt.",
                "Radial allowance added to the roller radius so the roller seats freely."), self.german)

        export = inputs.addTabCommandInput("export_tab", t("export")).children
        export.addBoolValueInput("save_local", t("save_local"), True, "", False)
        default_folder = str(pathlib.Path.home() / "Documents" / "MakeOrbit GearGenerator Exports")
        export.addStringValueInput("export_folder", t("folder"), default_folder)
        export.addBoolValueInput("send_makeorbit", t("makeorbit"), True, "", False)
        for key in ("step", "stl", "3mf", "dxf"):
            export.addBoolValueInput("format_" + key, t("format_" + key), True, "", key in {"step", "3mf"})
        export.addTextBoxCommandInput("makeorbit_note", "", t("makeorbit_note"), 2, True)
        inputs.addTextBoxCommandInput("calculated_summary", t("summary"), "", 6, True)

        changed = InputChangedHandler(self.german); command.inputChanged.add(changed); _handlers.append(changed)
        validate = ValidateHandler(self.german); command.validateInputs.add(validate); _handlers.append(validate)
        execute = ExecuteHandler(self.german); command.execute.add(execute); _handlers.append(execute)
        preview_handler = PreviewHandler(); command.executePreview.add(preview_handler); _handlers.append(preview_handler)
        destroy = DestroyHandler(); command.destroy.add(destroy); _handlers.append(destroy)
        _set_visibility(inputs); _update_summary(inputs, self.german)


class InputChangedHandler(adsk.core.InputChangedEventHandler):
    def __init__(self, german):
        super().__init__(); self.german = german

    def notify(self, args):
        inputs = args.inputs
        _set_visibility(inputs)
        _update_summary(inputs, self.german)


class ValidateHandler(adsk.core.ValidateInputsEventHandler):
    def __init__(self, german):
        super().__init__(); self.german = german

    def notify(self, args):
        try:
            calculate(_request(args.inputs)); args.areInputsValid = True
        except Exception:
            args.areInputsValid = False


class ExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self, german):
        super().__init__(); self.german = german

    def notify(self, args):
        app = adsk.core.Application.get(); ui = app.userInterface
        t = translator("de" if self.german else "en")
        try:
            request = _request(args.command.commandInputs)
            result = calculate(request)
            component, body, sketch = _create_solid(app, result, args.command.commandInputs.itemById("component_name").value)
            paths, notes = _export(app, args.command.commandInputs, component, body, sketch, result)
            detail = _summary(result, self.german).replace("<br>", "\n")
            if paths: detail += "\n\n" + "\n".join(paths)
            if notes: detail += "\n\n" + "\n".join(notes)
            ui.messageBox(t("created") + "\n\n" + detail)
        except Exception as error:
            try:
                app.log(traceback.format_exc())
            except Exception:
                pass
            ui.messageBox(t("error") + ":\n" + _error_text(error, self.german))


class PreviewHandler(adsk.core.CommandEventHandler):
    def notify(self, args):
        inputs = args.command.commandInputs
        if not inputs.itemById("preview_enabled").value:
            return
        try:
            result = calculate(_request(inputs))
            _create_solid(adsk.core.Application.get(), result, inputs.itemById("component_name").value)
            # Export is intentionally excluded from previews, so final execute
            # must still run when the user confirms the command.
            args.isValidResult = False
        except Exception:
            args.isValidResult = False


class DestroyHandler(adsk.core.CommandEventHandler):
    def notify(self, args):
        # Event handlers are retained for the add-in lifetime for Fusion stability.
        pass


def _create_solid(app, result, name):
    design = adsk.fusion.Design.cast(app.activeProduct)
    if not design:
        app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
        design = adsk.fusion.Design.cast(app.activeProduct)
    occurrence = design.rootComponent.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    component = occurrence.component; component.name = name or "MakeOrbit-Gear"
    sketch = component.sketches.add(component.xYConstructionPlane); sketch.name = component.name + " Profile"
    sketch.isComputeDeferred = True
    points = outline(result)
    lines = sketch.sketchCurves.sketchLines
    for index, current in enumerate(points):
        nxt = points[(index + 1) % len(points)]
        lines.addByTwoPoints(adsk.core.Point3D.create(current[0] / 10.0, current[1] / 10.0, 0),
                           adsk.core.Point3D.create(nxt[0] / 10.0, nxt[1] / 10.0, 0))
    circles = sketch.sketchCurves.sketchCircles
    if result.kind == "internal":
        circles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), result.outside_radius / 10.0)
    elif result.bore_radius is not None:
        circles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), result.bore_radius / 10.0)
    sketch.isComputeDeferred = False
    if sketch.profiles.count == 0:
        raise GearError("Fusion could not resolve a closed profile")
    profiles = [sketch.profiles.item(i) for i in range(sketch.profiles.count)]
    profiles_with_holes = [item for item in profiles if item.profileLoops.count >= 2]
    profile = max(profiles_with_holes or profiles, key=lambda item: item.areaProperties().area)
    extrude = component.features.extrudeFeatures.addSimple(
        profile, adsk.core.ValueInput.createByString("%.8g mm" % result.thickness),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    body = extrude.bodies.item(0); body.name = component.name
    component.attributes.add("MakeOrbit-GearGenerator", "parameters", json.dumps(result.as_dict(), sort_keys=True))
    return component, body, sketch


def _export(app, inputs, component, body, sketch, result):
    if not inputs.itemById("save_local").value and not inputs.itemById("send_makeorbit").value:
        return [], []
    folder = inputs.itemById("export_folder").value.strip()
    temporary = False
    if not inputs.itemById("save_local").value:
        folder = tempfile.mkdtemp(prefix="MakeOrbit-Gear-"); temporary = True
    os.makedirs(folder, exist_ok=True)
    stem = "".join(c if c.isalnum() or c in "-_" else "-" for c in component.name).strip("-") or "MakeOrbit-Gear"
    design = adsk.fusion.Design.cast(app.activeProduct); manager = design.exportManager
    created, notes = [], []
    makeorbit_notice_shown = False
    german = language_from_fusion(app) == "de"
    for extension in ("step", "stl", "3mf", "dxf"):
        if not inputs.itemById("format_" + extension).value:
            continue
        path = os.path.join(folder, stem + "." + extension)
        if extension == "step": options = manager.createSTEPExportOptions(path, component); ok = manager.execute(options)
        elif extension == "stl":
            options = manager.createSTLExportOptions(body, path); options.sendToPrintUtility = False; ok = manager.execute(options)
        elif extension == "3mf":
            options = manager.createC3MFExportOptions(body, path); options.sendToPrintUtility = False; ok = manager.execute(options)
        else:
            # saveAsDXF remains the widest compatible API. The replacement API is
            # still marked Preview by Autodesk and is unsuitable for distribution.
            ok = sketch.saveAsDXF(path)
        if not ok or not os.path.isfile(path):
            notes.append("Export failed: " + extension.upper()); continue
        created.append(path)
        if inputs.itemById("send_makeorbit").value:
            try:
                send_file(ADDIN_DIR, path, result, getattr(app.activeDocument, "name", "Fusion"))
                notes.append("MakeOrbit: " + os.path.basename(path))
            except MakeOrbitError as error:
                notes.append(str(error))
                if not makeorbit_notice_shown:
                    _show_makeorbit_unavailable(app.userInterface, german)
                    makeorbit_notice_shown = True
    if temporary:
        notes.append("Temporary export folder: " + folder)
    return created, notes


def run(context):
    global _definition, _control
    app = adsk.core.Application.get(); ui = app.userInterface
    german = language_from_fusion(app) == "de"; t = translator("de" if german else "en")
    _definition = ui.commandDefinitions.itemById(COMMAND_ID)
    if not _definition:
        _definition = ui.commandDefinitions.addButtonDefinition(COMMAND_ID, t("command"), t("description"), RESOURCE_DIR)
    created = CommandCreatedHandler(german); _definition.commandCreated.add(created); _handlers.append(created)
    workspace = ui.workspaces.itemById(WORKSPACE_ID)
    panel = workspace.toolbarPanels.itemById(PANEL_ID) if workspace else None
    if panel:
        _control = panel.controls.itemById(COMMAND_ID) or panel.controls.addCommand(_definition)
        _control.isPromoted = True


def stop(context):
    global _definition, _control
    if _control:
        try: _control.deleteMe()
        except Exception: pass
    if _definition:
        try: _definition.deleteMe()
        except Exception: pass
    _control = None; _definition = None; _handlers.clear()
