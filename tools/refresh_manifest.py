#!/usr/bin/env python3
"""Refresh integrity metadata only after intentional, reviewed repository edits.

This does not authorize uploads, remove personal data, or validate ROS runtime.
Requires Git to list tracked and non-ignored new files; ignores generated caches.
"""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = "metadata/MANIFEST.json"
SUPPLEMENTS = [
    "urdf/gazebo/myrobot_laser_step7.xacro",
    "urdf/gazebo/gazebo_sensor/lesson14_laser_step7.xacro",
    "launch/myrobot_laser_step7.launch",
    "urdf/gazebo/myrobot_tf_step8.xacro",
    "launch/myrobot_tf_step8.launch",
    "config/lesson14_scan_step8.rviz",
    "urdf/gazebo/myrobot_camera_step9.xacro",
    "urdf/gazebo/gazebo_sensor/lesson14_camera_step9.xacro",
    "launch/myrobot_camera_step9.launch",
    "config/lesson14_camera_step9.rviz",
    "scripts/cloud_preview_step9a.py",
    "config/lesson14_cloud_preview_step9a.rviz",
]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    provenance_path = ROOT / "metadata/SOURCE_PROVENANCE.json"
    provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
    provenance["last_update_date_china"] = "2026-10-16"
    provenance["active_code_snapshot_basis"] = (
        "Original rcdp plus delivered step4/6 and twelve step7/8/9/9a supplemental "
        "source/config files plus the user-requested classroom indoor world; "
        "not a fresh VM disk read-back. Original course packages stay in reference."
    )
    provenance["public_update_2026_10_16"] = {
        "scope_applies_to_commit": "91ceab5",
        "scope": "Sanitized notes and supplemental implementation/configuration only",
        "course_original_archives_world_screenshots_raw_logs_added": False,
        "new_source_files": [
            {"path": "catkin_ws/src/rcdp/" + name,
             "sha256": digest(ROOT / "catkin_ws/src/rcdp" / name)}
            for name in SUPPLEMENTS
        ],
        "whole_repository_history_sanitized": False,
        "rights_note": "No blanket open-source license or redistribution right for historical course material is granted."
    }
    resource_path = ROOT / "metadata/RESOURCE_INDEX_2026-10-16.json"
    if resource_path.is_file():
        resource = json.loads(resource_path.read_text(encoding="utf-8"))
        provenance["followup_user_requested_project_resources"] = {
            "resource_index": resource_path.relative_to(ROOT).as_posix(),
            "latest_course_pdfs_already_present_same_bytes": len(resource["courseware_latest_supplied"]),
            "new_archives_and_world": resource["new_binary_and_world_assets"],
            "new_screenshots": resource["new_screenshots"],
            "original_text_attachments": resource["original_user_text_attachments"],
            "user_terminal_record_count": len(resource["extracted_user_terminal_records"]),
            "internal_session_or_credentials_exported": False
        }
    provenance_path.write_text(json.dumps(provenance, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    listed = subprocess.check_output(
        ["git", "-c", "core.quotepath=false", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=ROOT
    ).decode("utf-8").split("\0")
    files = []
    for name in sorted(set(filter(None, listed))):
        if name == MANIFEST:
            continue
        path = ROOT / name
        if not path.is_file() or path.is_symlink():
            raise SystemExit("Expected regular repository file: " + name)
        files.append({"path": name, "bytes": path.stat().st_size, "sha256": digest(path)})
    result = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "date_china": "2026-10-16",
        "manifest_excludes_itself": True,
        "files": files
    }
    (ROOT / MANIFEST).write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Updated integrity manifest for %d files; no upload performed." % len(files))


if __name__ == "__main__":
    main()
