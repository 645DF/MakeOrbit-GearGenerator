# MakeOrbit GearGenerator for Autodesk Fusion

MakeOrbit GearGenerator creates parametric external involute gears, internal ring gears, and roller-chain sprockets as extruded Fusion components. Tooth count is the only mandatory sizing value; any additional dimensions you enable are used to derive and cross-check the remaining geometry.

The interface follows Fusion's language: German when Fusion is set to German, English for every other Fusion language. Every setting has a progressive tooltip and a compact 3D-style diagram.

## Main features

- External involute gears with configurable pressure angle and backlash
- Internal gearing with a calculated or explicit ring wall
- Roller-chain sprockets from link pitch, link width, roller diameter, roller thickness, optional connector wall, and clearance
- Closed gear by default; a centre bore is created only when explicitly enabled
- Exact pitch, outside, and root-radius calculations; rounded radial crowns and roller-seat pockets
- Extruded solid in a new named Fusion component
- Local STEP, STL, 3MF, and DXF export
- Authenticated loopback transfer to 645DF MakeOrbit using its existing Fusion bridge
- macOS and Windows installers, plus manual installation instructions

## Quick installation

### macOS

1. Download and unzip the release.
2. Double-click `installers/Install MakeOrbit GearGenerator.command`.
3. Restart Fusion, or open **Utilities > Add-ins > Scripts and Add-ins** and start **MakeOrbitGearGenerator**.

### Windows

1. Download and unzip the release.
2. Right-click `installers/Install-MakeOrbitGearGenerator.ps1` and choose **Run with PowerShell**.
3. Restart Fusion, or start the add-in through **Utilities > Add-ins > Scripts and Add-ins**.

The installers copy only this add-in to Fusion's user AddIns directory. They do not require administrator rights.

## MakeOrbit transfer

MakeOrbit must be open and its own Fusion integration must have been installed once. The generator reads the sibling bridge configuration and connects only to `127.0.0.1`, `localhost`, or `::1`. STEP, STL, and 3MF work with MakeOrbit 2.9.8; direct DXF storage is supported by MakeOrbit 2.9.9 or newer.

If MakeOrbit is unavailable, the add-in shows one unobtrusive information dialog per import attempt. On macOS, users may choose to open the [MakeOrbit beta page](https://645df.de/makeorbit-beta). On Windows, the dialog explains that a Windows version is planned. Local exports are retained in either case.

## Development and tests

The calculation module is deliberately independent of Autodesk modules:

```bash
cd MakeOrbitGearGenerator
python3 -m unittest discover -s tests -v
```

## Documentation

- [Bilingual PDF guide](docs/MakeOrbit_GearGenerator_Anleitung_DE_EN.pdf)
- [Editable guide source](docs/USER_GUIDE_DE_EN.md)

## License — source available, not open source

Copyright (c) 2026 Michael Jäger / 645DF. Private, non-commercial use of an unmodified official release is permitted. Copying, modifying, redistributing, embedding the code in another function or application, or using it commercially is prohibited without prior written permission. Paid commercial or integration rights may be negotiated separately. See [LICENSE](LICENSE) for the binding terms.
