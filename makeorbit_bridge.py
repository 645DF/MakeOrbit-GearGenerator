"""Client for MakeOrbit's authenticated loopback-only Fusion bridge."""

import base64
import json
import os
import pathlib
import urllib.error
import urllib.request
import uuid


class MakeOrbitError(RuntimeError):
    pass


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
