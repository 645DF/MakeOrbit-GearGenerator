"""Client for MakeOrbit's authenticated loopback-only Fusion bridge."""

import base64
import json
import os
import pathlib
import urllib.error
import urllib.request
import uuid


MAKEORBIT_BETA_URL = "https://645df.de/makeorbit-beta"


class MakeOrbitError(RuntimeError):
    pass


def unavailable_guidance(system_name, german):
    """Return localized, platform-specific help when direct import is unavailable."""
    if system_name == "Darwin":
        if german:
            message = (
                "MakeOrbit wurde auf diesem Mac nicht gefunden oder ist nicht erreichbar.\n\n"
                "Die erzeugten Dateien bleiben lokal gespeichert. Wenn du MakeOrbit ausprobieren "
                "möchtest, findest du auf 645df.de Informationen zum aktuellen macOS-Betatest.\n\n"
                "MakeOrbit-Seite jetzt öffnen?"
            )
        else:
            message = (
                "MakeOrbit was not found on this Mac or could not be reached.\n\n"
                "The generated files remain saved locally. If you would like to try MakeOrbit, "
                "645df.de has information about the current macOS beta test.\n\n"
                "Open the MakeOrbit page now?"
            )
        return message, MAKEORBIT_BETA_URL

    if system_name == "Windows":
        message = (
            "MakeOrbit wurde auf diesem Windows-PC nicht gefunden oder ist nicht erreichbar.\n\n"
            "Die erzeugten Dateien bleiben lokal gespeichert. Eine Windows-Version von MakeOrbit ist in Planung."
            if german else
            "MakeOrbit was not found on this Windows PC or could not be reached.\n\n"
            "The generated files remain saved locally. A Windows version of MakeOrbit is planned."
        )
        return message, None

    message = (
        "MakeOrbit wurde nicht gefunden oder ist nicht erreichbar. Die erzeugten Dateien bleiben lokal gespeichert."
        if german else
        "MakeOrbit was not found or could not be reached. The generated files remain saved locally."
    )
    return message, None


def config_candidates(addin_dir):
    result = [pathlib.Path(addin_dir).parent / "MakeOrbitFusion" / "bridge_config.json"]
    if os.name == "nt":
        appdata = os.environ.get("APPDATA")
        if appdata:
            result.append(pathlib.Path(appdata) / "Autodesk" / "Autodesk Fusion 360" / "API" / "AddIns" / "MakeOrbitFusion" / "bridge_config.json")
    else:
        result.append(pathlib.Path.home() / "Library" / "Application Support" / "Autodesk" / "Autodesk Fusion 360" / "API" / "AddIns" / "MakeOrbitFusion" / "bridge_config.json")
    return result


def load_config(addin_dir):
    for path in config_candidates(addin_dir):
        try:
            config = json.loads(path.read_text(encoding="utf-8"))
            if config.get("token") and config.get("host", "127.0.0.1") in {"127.0.0.1", "localhost", "::1"}:
                return config
        except (OSError, ValueError):
            continue
    raise MakeOrbitError("MakeOrbit bridge configuration was not found. Install its Fusion integration first.")


def send_file(addin_dir, path, result, source_document="Fusion", project_id=None):
    config = load_config(addin_dir)
    path = pathlib.Path(path)
    metadata = {
        "exportID": str(uuid.uuid4()), "designName": path.stem,
        "sourceDocumentName": source_document, "bodyCount": 1,
        "projectID": project_id, "projectName": None,
        "format": path.suffix.lstrip(".").lower(), "filename": path.name,
        "recordType": "gear",
    }
    encoded = base64.b64encode(json.dumps(metadata, ensure_ascii=False).encode("utf-8")).decode("ascii")
    request = urllib.request.Request(
        "http://%s:%d/v1/import" % (config.get("host", "127.0.0.1"), int(config.get("port", 64536))),
        data=path.read_bytes(), method="POST",
        headers={"X-MakeOrbit-Token": str(config["token"]), "X-MakeOrbit-Metadata": encoded,
                 "Content-Type": "application/octet-stream", "Connection": "close"},
    )
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            return json.loads(response.read().decode("utf-8") or "{}")
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise MakeOrbitError("MakeOrbit rejected %s (HTTP %d): %s" % (path.name, error.code, detail)) from error
    except OSError as error:
        raise MakeOrbitError("MakeOrbit is not reachable. Open MakeOrbit and try again: %s" % error) from error
