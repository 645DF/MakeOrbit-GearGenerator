#!/bin/zsh
set -eu

SCRIPT_DIR="${0:A:h}"
SOURCE_DIR="${SCRIPT_DIR:h}"
TARGET_ROOT="${HOME}/Library/Application Support/Autodesk/Autodesk Fusion 360/API/AddIns"
TARGET_DIR="${TARGET_ROOT}/MakeOrbitGearGenerator"

mkdir -p "$TARGET_ROOT"
if [[ -d "$TARGET_DIR" ]]; then
  BACKUP_DIR="${TARGET_DIR}.previous"
  rm -rf "$BACKUP_DIR"
  mv "$TARGET_DIR" "$BACKUP_DIR"
fi
ditto --noqtn "$SOURCE_DIR" "$TARGET_DIR"
rm -rf "$TARGET_DIR/.git" "$TARGET_DIR/__pycache__" "$TARGET_DIR/tests/__pycache__"
echo "MakeOrbit GearGenerator installed at:"
echo "$TARGET_DIR"
echo "Restart Autodesk Fusion or start the add-in from Scripts and Add-ins."
read -k 1 "?Press any key to close."
