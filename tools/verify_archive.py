#!/usr/bin/env python3
"""Verify handoff file integrity (stdlib only, NOT a Gazebo runtime test)."""
from pathlib import Path
import ast
import hashlib
import json
import sys
import zipfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


def main():
    manifest = json.loads((ROOT / "metadata/MANIFEST.json").read_text(encoding="utf-8"))
    errors = []
    for item in manifest["files"]:
        path = ROOT / item["path"]
        if not path.is_file():
            errors.append("Missing: " + item["path"])
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != item["sha256"] or path.stat().st_size != item["bytes"]:
            errors.append("Changed: " + item["path"])
    inventory = json.loads((ROOT / "metadata/COURSEWARE_INVENTORY.json").read_text(encoding="utf-8"))
    if len(inventory["files"]) != 15 or sum(x["pages"] for x in inventory["files"]) != 1682:
        errors.append("Courseware inventory differs")
    for path in (ROOT / "catkin_ws/src/rcdp").rglob("*"):
        if path.suffix in (".xml", ".urdf", ".xacro", ".launch", ".world"):
            ET.parse(path)
        elif path.suffix == ".py":
            ast.parse(path.read_text(encoding="utf-8"))
    for path in ROOT.rglob("*.zip"):
        if ".git" in path.relative_to(ROOT).parts:
            continue
        with zipfile.ZipFile(path) as archive:
            if archive.testzip() is not None:
                errors.append("ZIP CRC failed: " + str(path))
    if errors:
        print("\n".join(errors))
        return 1
    print(f"PASS: {len(manifest['files'])} files match SHA256; 15 course PDFs / 1682 recorded pages; XML/Python syntax and ZIP CRC valid.")
    print("This is archive/static verification, not a ROS/Gazebo runtime test.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
