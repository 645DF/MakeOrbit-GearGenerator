# MakeOrbit GearGenerator - Anleitung / User Guide

## Deutsch

### Zweck und Funktionsumfang

MakeOrbit GearGenerator erzeugt in Autodesk Fusion ein neues, extrudiertes Konstruktionsteil. Unterstützt werden Außenverzahnungen, Innenverzahnungen und Kettenräder. Die Zähnezahl ist die einzige Pflichtangabe. Ohne weitere Größenangabe verwendet der Generator Modul 2 mm; jede aktivierte Maßvorgabe ersetzt beziehungsweise überprüft diese Herleitung.

### Installation auf macOS

1. GitHub-Release laden und vollständig entpacken.
2. `Install MakeOrbit GearGenerator.command` im Ordner `installers` doppelklicken.
3. Falls macOS nachfragt, den Start des lokalen Skripts bestätigen.
4. Fusion neu starten. Alternativ in Fusion **Dienstprogramme > Zusatzmodule > Skripte und Zusatzmodule** öffnen und `MakeOrbitGearGenerator` starten.
5. Der Befehl **MakeOrbit GearGenerator** erscheint im Bereich **Volumenkörper > Erstellen**.

Manuell: Den vollständigen Ordner `MakeOrbitGearGenerator` nach `~/Library/Application Support/Autodesk/Autodesk Fusion 360/API/AddIns/` kopieren.

### Installation unter Windows

1. GitHub-Release laden und vollständig entpacken.
2. `Install-MakeOrbitGearGenerator.ps1` im Ordner `installers` mit PowerShell ausführen.
3. Fusion neu starten oder das Zusatzmodul über **Dienstprogramme > Zusatzmodule > Skripte und Zusatzmodule** starten.

Manuell: Den vollständigen Ordner `MakeOrbitGearGenerator` nach `%APPDATA%\Autodesk\Autodesk Fusion 360\API\AddIns\` kopieren.

### Bedienung

1. Zahnradtyp wählen: Außenverzahnung, Innenverzahnung oder Kettenrad.
2. Zähnezahl eingeben. Sie muss mindestens 8 betragen, beim Kettenrad mindestens 6.
3. Optional einen Innenradius aktivieren. Bleibt er deaktiviert, entsteht ein geschlossenes Zahnrad.
4. Unter **Optionale Maße** nur die Werte aktivieren, die fest vorgegeben werden sollen. Widersprüchliche Angaben werden vor dem Erzeugen abgelehnt.
5. Für Kettenräder Kettengliedlänge/Teilung, innere Breite, Röllchendurchmesser und Röllchendicke eingeben. Die optionale Verbinderwand wird beidseitig von der nutzbaren Dicke abgezogen. Der Rollensitzradius ist `R = Röllchendurchmesser / 2 + Rollenspiel`.
6. Unter **Export & MakeOrbit** die gewünschten Formate wählen.
7. Mit **OK** wird ein neues Fusion-Bauteil mit Profilskizze und extrudiertem Körper erzeugt.

### Maßlogik

- Modul `m = Teilkreisdurchmesser / Zähnezahl`
- Kreisteilung `p = π × m`
- Außenrad: Standard-Außenradius `r_a = r_p + m`, Standard-Fußradius `r_f = r_p - 1,25m`
- Innenrad: Zahnspitzen zeigen nach innen; die Ringwand liegt außerhalb des Zahnfußes
- Kettenrad: Teilkreisradius `r_p = p / (2 × sin(π / z))`
- Zahnspitzen und Zahnfüße werden als radiale Bogenabschnitte erzeugt; Kettenrollen sitzen in berechneten Kreisbogentaschen

### MakeOrbit

MakeOrbit vor der Übergabe öffnen und dessen Fusion-Integration einmal installieren. Die Übertragung bleibt lokal auf dem Computer und verwendet die von MakeOrbit erzeugte Token-Datei. STEP, STL und 3MF werden ab MakeOrbit 2.9.8 angenommen; DXF wird ab MakeOrbit 2.9.9 direkt gespeichert.

Ist MakeOrbit nicht installiert oder nicht erreichbar, erscheint pro Importversuch nur ein dezenter Hinweis. Unter macOS kann auf Wunsch die Seite `https://645df.de/makeorbit-beta` mit Informationen zum aktuellen Betatest geöffnet werden. Unter Windows informiert das Fenster darüber, dass eine Windows-Version geplant ist. Bereits erzeugte lokale Exportdateien bleiben erhalten.

### Lizenz

Der öffentlich einsehbare Quellcode ist **nicht Open Source**. Eine unveränderte offizielle Version darf privat und nichtkommerziell verwendet werden. Kopieren, Verändern, Weitergeben, Einbauen oder Wiederverwenden in anderen Funktionen oder Apps und jede kommerzielle Nutzung sind ohne vorherige schriftliche Erlaubnis von Michael Jäger / 645DF untersagt. Bezahlte Sonder- oder Nutzungslizenzen können individuell vereinbart werden. Maßgeblich ist die Datei `LICENSE` im GitHub-Repository.

### Fehlerbehebung

- **Befehl fehlt:** Fusion neu starten und unter Skripte und Zusatzmodule prüfen, ob das Zusatzmodul läuft.
- **Maße widersprechen sich:** Nur eine leitende Größe vorgeben oder Werte so anpassen, dass sie innerhalb 2 % dasselbe Modul ergeben.
- **MakeOrbit nicht erreichbar:** MakeOrbit öffnen und dessen Fusion-Integration erneut installieren.
- **Profil nicht geschlossen:** Zähnezahl erhöhen oder extreme Kombinationen aus Spiel, Modul und Durchmessern vermeiden.

## English

### Purpose and scope

MakeOrbit GearGenerator creates a new extruded component in Autodesk Fusion. It supports external involute gears, internal ring gears, and roller-chain sprockets. Tooth count is the only required input. If no physical size is supplied, the generator uses a 2 mm module; every enabled dimension overrides or cross-checks that derivation.

### Installation on macOS

1. Download and fully extract the GitHub release.
2. Double-click `Install MakeOrbit GearGenerator.command` in `installers`.
3. Confirm the local script if macOS asks.
4. Restart Fusion. Alternatively open **Utilities > Add-ins > Scripts and Add-ins** and start `MakeOrbitGearGenerator`.
5. **MakeOrbit GearGenerator** appears under **Solid > Create**.

Manual installation: copy the complete `MakeOrbitGearGenerator` folder to `~/Library/Application Support/Autodesk/Autodesk Fusion 360/API/AddIns/`.

### Installation on Windows

1. Download and fully extract the GitHub release.
2. Run `Install-MakeOrbitGearGenerator.ps1` from `installers` with PowerShell.
3. Restart Fusion or start the add-in from **Utilities > Add-ins > Scripts and Add-ins**.

Manual installation: copy the complete `MakeOrbitGearGenerator` folder to `%APPDATA%\Autodesk\Autodesk Fusion 360\API\AddIns\`.

### Operation

1. Select external gear, internal gear, or chain sprocket.
2. Enter the tooth count. The minimum is 8, or 6 for sprockets.
3. Optionally enable a bore radius. When disabled, the gear remains closed.
4. Under **Optional dimensions**, enable only values that must be fixed. Conflicting inputs are rejected before construction.
5. For sprockets, enter chain link length/pitch, inside width, roller diameter, and roller thickness. The optional connector wall is subtracted on both sides. Roller-seat radius is `R = roller diameter / 2 + roller clearance`.
6. Select output formats under **Export & MakeOrbit**.
7. Press **OK** to create a new Fusion component containing the profile sketch and extruded solid.

### Dimension logic

- Module `m = pitch diameter / tooth count`
- Circular pitch `p = π × m`
- External gear defaults: addendum radius `r_a = r_p + m`, root radius `r_f = r_p - 1.25m`
- Internal gear tooth tips point inward and the ring wall is outside the tooth root
- Sprocket pitch radius `r_p = p / (2 × sin(π / z))`
- Tooth tips and roots use radial arcs; chain rollers sit in calculated circular pockets

### MakeOrbit

Open MakeOrbit and install its Fusion integration once. Transfer stays on the computer and uses MakeOrbit's generated token file. MakeOrbit 2.9.8 accepts STEP, STL, and 3MF; MakeOrbit 2.9.9 or newer also stores DXF directly.

If MakeOrbit is not installed or cannot be reached, the add-in shows only one unobtrusive notice per import attempt. On macOS, the user may open `https://645df.de/makeorbit-beta` for information about the current beta test. On Windows, the dialog explains that a Windows version is planned. Existing local export files are retained.

### License

The publicly visible source code is **not open source**. An unmodified official release may be used privately and non-commercially. Copying, modifying, redistributing, embedding, or reusing the code in another function or app, and any commercial use, are prohibited without prior written permission from Michael Jäger / 645DF. Paid special-purpose or commercial licenses may be negotiated separately. The `LICENSE` file in the GitHub repository contains the binding terms.

### Troubleshooting

- **Command is missing:** Restart Fusion and confirm that the add-in is running under Scripts and Add-ins.
- **Dimensions conflict:** Specify one leading size or adjust values so they imply the same module within 2%.
- **MakeOrbit is unreachable:** Open MakeOrbit and reinstall its Fusion integration.
- **Profile is not closed:** Increase tooth count or avoid extreme combinations of backlash, module, and diameters.
