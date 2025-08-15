#!/usr/bin/env python3
import os
import sys
import subprocess

# Get the folder of this script
base_dir = os.path.dirname(os.path.abspath(__file__))

# Path to deps folder
deps_path = os.path.join(base_dir, "deps")

# Prepend deps folder to PYTHONPATH
pythonpath = os.environ.get("PYTHONPATH", "")
pythonpath = f"{deps_path}:{pythonpath}" if pythonpath else deps_path
os.environ["PYTHONPATH"] = pythonpath

# Path to the main SubScout script
subscout_script = os.path.join(base_dir, "subscout.py")

# Pass all command line arguments to subscout.py
args = [sys.executable, subscout_script] + sys.argv[1:]

# Run SubScout
sys.exit(subprocess.call(args))
