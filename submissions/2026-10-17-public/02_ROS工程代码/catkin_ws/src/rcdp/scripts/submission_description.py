#!/usr/bin/env python3
"""Packaging helper: expand unchanged source; change ONE drive library path only.
No ROS node, services or running simulation is modified. ROS Noetic devel layout.
"""
import argparse
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET

def relocate(xml_text, library):
    root = ET.fromstring(xml_text)
    plugins = [p for p in root.findall('.//plugin')
               if p.get('name') == 'lesson14_four_wheel_drive']
    if len(plugins) != 1:
        raise ValueError('Expected exactly one four-wheel drive plugin')
    if Path(plugins[0].get('filename', '')).name != 'librcdp_4wd_stampfix.so':
        raise ValueError('Unexpected original drive library')
    plugins[0].set('filename', str(library))
    return ET.tostring(root, encoding='unicode')

def main():
    p = argparse.ArgumentParser()
    p.add_argument('model')
    p.add_argument('library')
    a = p.parse_args()
    library = Path(a.library).resolve()
    if not library.is_file():
        raise SystemExit('Build this workspace first; missing: ' + str(library))
    result = subprocess.run(['rosrun','xacro','xacro',a.model],
                            check=True, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, universal_newlines=True)
    if result.stderr:
        sys.stderr.write(result.stderr)
    print(relocate(result.stdout, library))

if __name__ == '__main__':
    main()
